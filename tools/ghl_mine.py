#!/usr/bin/env python3
"""Mine every SMS copy variant a client has actually run, out of GoHighLevel.

WHY THIS EXISTS
  Copy is edited *in place* inside GHL workflows, so a workflow only ever holds its
  CURRENT text — every variant you overwrote is gone from it. GHL's Workflows API
  exposes no message content at all (verified against their OpenAPI spec, v2 and v3:
  GET /workflows/ returns only id/name/status/version/dates). The sent-message log is
  therefore the ONLY surviving record of what was actually tested.

THE DOMAIN MODEL (do not change without reading references/domain-model.md)
  - Scaletopia ships TWO texts at once (T1 + T2, ~13s apart). The BATCH is the atomic
    unit of copy, exactly as sms-playbook/winners.csv stores it (raw_T1, raw_T2).
    Scoring T1 and T2 separately makes T1 look like it earns ~0% replies. Never do it.
  - Batch #1 = initial send. Batch #2 = retargeting (median ~54 days later).
  - Replies/opt-outs are attributed at the PROSPECT level to the batch that preceded them.
  - Judge reply % against opt-out %. A variant whose opt-out rate >= its reply rate is a
    list-burner, not a winner.

USAGE
  python tools/ghl_mine.py --client digital-resource
  python tools/ghl_mine.py --client kynship --out "clients/kynship/output"

Credentials are read from the MCP servers already configured in ~/.claude.json, so no
secrets live in this repo. Override with --pit / --location if you need to.
"""
import argparse, collections, csv, datetime as dt, json, os, re, sys, time
import urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://services.leadconnectorhq.com"
V_CONV, V_CONTACT, V_LOC = "2021-04-15", "2021-07-28", "2021-07-28"
BATCH_GAP_S = 300          # texts within 5 min of each other = one batch (one copy unit)
WORKERS     = 8
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY    = os.path.join(ROOT, "clients", "registry.json")

# Merge-field slots we strip back out. Resolved per-location by fieldKey, because GHL
# mints DIFFERENT custom-field IDs per sub-account — hardcoding IDs silently breaks
# the de-merge on every other client.
FIELD_KEYS = ["workflow_name", "workflow_id", "copy_variant", "competitor_1", "competitor_2",
              "case_study_1", "case_study_2", "ai_first_line", "company", "service",
              "niche", "niche_label", "title"]
STANDARD   = ["firstName", "lastName", "companyName", "city", "state"]
# longest values substituted first, so "Mr Rooter Plumbing" masks before "Mr Rooter"
SLOT_ORDER = ["ai_first_line", "companyName", "company", "case_study_1", "case_study_2",
              "competitor_1", "competitor_2", "niche_label", "service", "niche",
              "firstName", "lastName", "city", "state", "title"]
STOP_RX = re.compile(r"^\s*(stop|unsubscribe|remove me|opt ?out|quit|end|cancel)\b", re.I)
T = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def creds_from_mcp(server):
    """Pull the Bearer token out of the MCP server we already configured."""
    p = os.path.expanduser("~/.claude.json")
    hdrs = (json.load(open(p)).get("mcpServers", {}).get(server, {}) or {}).get("headers", {})
    auth = hdrs.get("Authorization", "")
    if not auth.startswith("Bearer "):
        sys.exit(f"No Bearer token for MCP server '{server}' in {p}. Pass --pit instead.")
    return auth[7:]


def req(pit, path, version, method="GET", query=None, body=None, tries=4):
    url = BASE + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        try:
            r = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": f"Bearer {pit}", "Version": version,
                "Content-Type": "application/json", "Accept": "application/json",
                # GHL's WAF 403s Python's default urllib user-agent
                "User-Agent": "curl/8.7.1"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if a == tries - 1:
                print(f"  !! {path} failed: {str(e)[:80]}", flush=True)
                return None
            time.sleep(1.5 * (a + 1))


# ---------------------------------------------------------------- fetch
def get_field_map(pit, loc):
    """fieldKey -> custom-field id, for THIS location."""
    d = req(pit, f"/locations/{loc}/customFields", V_LOC) or {}
    m = {}
    for f in d.get("customFields", []):
        key = (f.get("fieldKey") or "").replace("contact.", "")
        if key in FIELD_KEYS:
            m[f["id"]] = key
    return m


def get_era(pit, loc, prefix):
    """Sub-accounts get REUSED. Scope to this client's own era or you mix in another
    business's copy. Era starts at the earliest workflow whose name matches the client."""
    d = req(pit, "/workflows/", V_CONV, query={"locationId": loc}) or {}
    wfs = d.get("workflows", [])
    mine = [w for w in wfs if w["name"].lower().startswith(prefix.lower())]
    if not mine:
        print(f"  !! no workflow starts with '{prefix}' — using all {len(wfs)} workflows")
        mine = wfs
    return min(w["createdAt"] for w in mine)[:10], wfs


def _contact_slice(pit, loc, gte, lt):
    """One dateAdded window, walked with searchAfter (page numbers hard-cap at 10,000)."""
    out, after = [], None
    flt = [{"field": "dateAdded", "operator": "range", "value": {"gte": gte, "lt": lt}}]
    while True:
        b = {"locationId": loc, "pageLimit": 500, "filters": flt}
        if after:
            b["searchAfter"] = after
        d = req(pit, "/contacts/search", V_CONTACT, "POST", body=b)
        if not d or not d.get("contacts"):
            break
        out += d["contacts"]
        after = d["contacts"][-1].get("searchAfter")
        if not after:
            break
    return out


def get_contacts(pit, loc):
    """We need EVERY contact that was messaged in-era — and a contact created long ago can
    still be messaged today (retargeting), so we cannot filter contacts to the era: that
    silently drops them. Instead pull all of them, but partition dateAdded into windows and
    fetch the windows in PARALLEL. searchAfter is sequential within a window; windows are not.
    (Leadgenix: 119k contacts, 313s serial -> ~50s this way.)"""
    d = req(pit, "/contacts/search", V_CONTACT, "POST", body={"locationId": loc, "pageLimit": 1})
    total = (d or {}).get("total", 0)
    if not total:
        return []
    now = dt.datetime.now(dt.timezone.utc)
    wins, y, m = [], 2019, 1                     # generous lower bound; empty windows cost ~1 call
    while (y, m) <= (now.year, now.month):
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        wins.append((f"{y}-{m:02d}-01T00:00:00.000Z", f"{ny}-{nm:02d}-01T00:00:00.000Z"))
        y, m = ny, nm
    wins.append((f"{now.year}-{now.month:02d}-01T00:00:00.000Z", "2099-01-01T00:00:00.000Z"))

    done = [0]
    def pull(w):
        c = _contact_slice(pit, loc, *w)
        done[0] += len(c)
        print(f"\r  contacts: {done[0]:,}/{total:,}", end="", flush=True)
        return c

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        chunks = list(ex.map(pull, wins))
    out = list({c["id"]: c for ch in chunks for c in ch}.values())
    print(f"\r  contacts: {len(out):,}/{total:,}" + (" ⚠ MISSING SOME" if len(out) < total * .99 else ""))
    return out


def get_messages(pit, loc, since):
    """Cursor pagination is sequential and slow (~5s/call), so split into monthly
    windows and pull them in parallel."""
    y0 = int(since[:4])
    now = dt.datetime.now(dt.timezone.utc)
    wins = []
    for y in range(y0, now.year + 1):
        for m in range(1, 13):
            ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
            s = f"{y}-{m:02d}-01T00:00:00.000Z"
            if s[:10] < since[:7] + "-01":
                continue
            wins.append((s, f"{ny}-{nm:02d}-01T00:00:00.000Z"))

    def pull(w):
        s, e = w
        acc, cur = [], None
        while True:
            q = {"locationId": loc, "limit": 1000, "channel": "SMS", "startDate": s, "endDate": e}
            if cur:
                q["cursor"] = cur
            d = req(pit, "/conversations/messages/export", V_CONV, query=q)
            if not d:
                break
            b = d.get("messages", [])
            acc += b
            cur = d.get("nextCursor")
            if not cur or not b:
                break
        return acc

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        chunks = list(ex.map(pull, wins))
    msgs = [m for c in chunks for m in c]
    return list({m["id"]: m for m in msgs}.values())


# ---------------------------------------------------------------- analyse
def demerge(body, c):
    """Substitute this contact's OWN merged values back out. Exact, not fuzzy — fuzzy
    similarity can't tell 'Hi Cindy'/'Hi Bartholomew' (same copy) from 'could I'/'can I'
    (a real test), and would silently merge two experiments into one.
    Word-boundary anchored: without \\b, title='Owner' turns 'homeowners' into
    'home{{title}}s'."""
    subs = [(str(c[k]).strip(), "{{%s}}" % k) for k in SLOT_ORDER
            if c.get(k) and isinstance(c.get(k), str) and len(str(c[k]).strip()) >= 3]
    subs.sort(key=lambda x: -len(x[0]))
    b = body or ""
    for v, ph in subs:
        b = re.sub(r"\b" + re.escape(v) + r"\b", ph, b, flags=re.I)
    return re.sub(r"\s+", " ", b).strip()


def analyse(contacts, msgs, era, fieldmap):
    CMAP = {}
    for c in contacts:
        d = {k: c.get(k) for k in STANDARD}
        d["tags"] = c.get("tags") or []
        for f in c.get("customFields", []):
            k = fieldmap.get(f.get("id"))
            if k:
                d[k] = f.get("value")
        CMAP[c["id"]] = d

    era_msgs = [m for m in msgs if m["dateAdded"][:10] >= era]
    out = sorted([m for m in era_msgs if m["direction"] == "outbound"], key=lambda m: m["dateAdded"])
    inb = sorted([m for m in era_msgs if m["direction"] == "inbound"], key=lambda m: m["dateAdded"])

    byc = collections.defaultdict(list)
    for m in out:
        if CMAP.get(m["contactId"]):
            byc[m["contactId"]].append(m)

    rep, opt = collections.defaultdict(list), collections.defaultdict(list)
    for m in inb:
        (opt if STOP_RX.match(m.get("body") or "") else rep)[m["contactId"]].append(m["dateAdded"])

    # group each prospect's texts into batches (a batch == one copy unit == T1+T2)
    S = collections.defaultdict(lambda: {"n":0,"rep":0,"opt":0,"deliv":0,"first":None,"last":None,
                                         "camp":collections.Counter(),"ex":None})
    nprospect = nbatch = 0
    for cid, ms in byc.items():
        c = CMAP[cid]
        nprospect += 1
        groups, cur = [], [ms[0]]
        for a, b in zip(ms, ms[1:]):
            if (T(b["dateAdded"]) - T(a["dateAdded"])).total_seconds() > BATCH_GAP_S:
                groups.append(cur); cur = [b]
            else:
                cur.append(b)
        groups.append(cur)
        nbatch += len(groups)
        for i, g in enumerate(groups):
            start = g[0]["dateAdded"]
            end   = groups[i+1][0]["dateAdded"] if i + 1 < len(groups) else "9999"
            key   = (min(i + 1, 3), tuple(demerge(m.get("body"), c) for m in g))
            e = S[key]; e["n"] += 1
            e["deliv"] += all(m["status"] == "delivered" for m in g)
            e["rep"]   += any(start < r < end for r in rep.get(cid, []))
            e["opt"]   += any(start < o < end for o in opt.get(cid, []))
            e["camp"][c.get("workflow_name") or "(unknown)"] += 1
            e["first"] = min(e["first"], start) if e["first"] else start
            e["last"]  = max(e["last"],  start) if e["last"]  else start
            if not e["ex"]:
                e["ex"] = [m.get("body") for m in g]

    POS = {1: "initial", 2: "retarget", 3: "retarget 3+"}
    rows = []
    for (pos, texts), e in S.items():
        n = e["n"]
        t1 = texts[0] if texts else ""
        t2 = " ⏎ ".join(texts[1:]) if len(texts) > 1 else ""
        rows.append({"send": POS[pos], "campaign": e["camp"].most_common(1)[0][0],
            "prospects": n, "replies": e["rep"], "reply_pct": round(100*e["rep"]/n, 2),
            "optouts": e["opt"], "optout_pct": round(100*e["opt"]/n, 2),
            "burner": e["opt"] >= e["rep"] and e["opt"] > 0,
            "delivered_pct": round(100*e["deliv"]/n, 1), "texts_in_batch": len(texts),
            "first_sent": e["first"][:10], "last_sent": e["last"][:10],
            "T1": t1, "T2": t2, "char_T1": len(t1), "char_T2": len(t2),
            "example_T1": (e["ex"] or [""])[0],
            "example_T2": (e["ex"] or ["", ""])[1] if len(e["ex"] or []) > 1 else ""})
    rows.sort(key=lambda r: -r["prospects"])
    return rows, {"prospects": nprospect, "batches": nbatch,
                  "outbound": len(out), "inbound": len(inb),
                  "no_contact": sum(1 for m in out if m["contactId"] not in CMAP)}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True, help="key in clients/registry.json")
    ap.add_argument("--out", help="output dir (default: from registry)")
    ap.add_argument("--pit"); ap.add_argument("--location")
    ap.add_argument("--since", help="YYYY-MM-DD — only mine from here (overrides the auto-detected "
                                    "era; use for long-tenured clients where you only want recent copy)")
    ap.add_argument("--min", type=int, default=20, help="min prospects to count as a real variant")
    a = ap.parse_args()

    reg = {k: v for k, v in json.load(open(REGISTRY)).items() if not k.startswith("_")}
    if a.client not in reg:
        sys.exit(f"'{a.client}' not in registry. Known: {', '.join(sorted(reg))}")
    cfg = reg[a.client]
    sms = cfg.get("sms") or {}
    if sms.get("platform") != "ghl":
        sys.exit(f"'{a.client}' has no GHL sms channel in the registry.")

    pit = a.pit or (creds_from_mcp(sms["mcp"]) if sms.get("mcp") else None)
    loc = a.location or sms.get("locationId")
    if not pit or not loc:
        sys.exit(f"'{a.client}' is missing a GHL token and/or locationId.\n"
                 f"  Create a read-only Private Integration Token in that sub-account, then:\n"
                 f"    claude mcp add --transport http --scope user ghl-{a.client} "
                 f"{BASE}/mcp/anthropic/v2 --header \"Authorization: Bearer pit-…\"\n"
                 f"  and fill in sms.mcp + sms.locationId in clients/registry.json.")

    out_dir = a.out or os.path.join(ROOT, cfg.get("output", f"clients/{a.client}/output"))
    os.makedirs(out_dir, exist_ok=True)
    label = cfg.get("label", a.client)
    cfg = {**sms, "label": label}

    print(f"[{label}] location {loc}")
    fmap = get_field_map(pit, loc)
    print(f"  custom fields resolved by fieldKey: {len(fmap)} ({', '.join(sorted(set(fmap.values())))})")
    if "workflow_name" not in fmap.values():
        print("  !! no contact.workflow_name field — campaign attribution will be weak")

    era, wfs = get_era(pit, loc, cfg.get("workflow_prefix", label))
    auto = era
    era = a.since or cfg.get("era_start") or era
    why = "--since" if a.since else ("registry era_start" if cfg.get("era_start") else "auto (earliest matching workflow)")
    print(f"  mining from {era}  [{why}]" + (f", account era begins {auto}" if era != auto else ""))
    print(f"  {len(wfs)} workflows in the account")

    t0 = time.time()
    contacts = get_contacts(pit, loc); print(f"    ({time.time()-t0:.0f}s)")
    t0 = time.time()
    msgs = get_messages(pit, loc, era); print(f"  messages: {len(msgs):,} ({time.time()-t0:.0f}s)")

    rows, st = analyse(contacts, msgs, era, fmap)
    real = [r for r in rows if r["prospects"] >= a.min]
    burners = [r for r in real if r["burner"]]

    with open(f"{out_dir}/sms-copy-history.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(real, open(f"{out_dir}/batches.json", "w"), indent=2)

    print(f"\n  {st['prospects']:,} prospects · {st['batches']:,} batches · "
          f"{st['outbound']:,} outbound / {st['inbound']:,} inbound")
    if st["no_contact"]:
        print(f"  !! {st['no_contact']:,} outbound had no contact record — check the era boundary")
    print(f"  {len(rows)} copy units ({len(real)} with >={a.min} prospects)")
    if burners:
        print(f"  ⚠ {len(burners)} LIST-BURNERS (opt-outs >= replies):")
        for r in sorted(burners, key=lambda r: -r["prospects"])[:3]:
            print(f"      {r['prospects']:>6,} prospects · reply {r['reply_pct']}% / opt-out {r['optout_pct']}%"
                  f"  {r['T1'][:52]}…")
    print("\n  TOP COPY (reply %, >=100 prospects):")
    for r in sorted([x for x in real if x["prospects"] >= 100], key=lambda x: -x["reply_pct"])[:5]:
        print(f"    reply {r['reply_pct']:5.2f}%  opt-out {r['optout_pct']:4.2f}%  {r['prospects']:>5,} · {r['send']}")
        print(f"       T1: {r['T1'][:88]}")
        print(f"       T2: {r['T2'][:88]}")
    print(f"\n  wrote {out_dir}/sms-copy-history.csv + batches.json")


if __name__ == "__main__":
    main()
