"""
calls_db.py — query the Supabase `client_calls` table from the CLI.

Use this whenever you (Claude or a human) need to pull sales-call transcripts
or categorized call metadata while building a GTM strategy. It is the canonical
way to read from the calls database — do not re-fetch transcripts from Fireflies
when the data is already here.

================================================================================
DATABASE CONTEXT — `client_calls` table (Supabase / Postgres)
================================================================================
One row per recorded sales/strategy call. Populated from Fireflies transcripts
that have been categorized (category, angle, pain point, etc.) by Claude.

Columns:
    id                bigserial PK
    client            text  — which agency/client this call belongs to
                              (e.g. 'kynship', 'unitzero'). ALWAYS filter by this.
    row_id            int   — original spreadsheet row number
    company           text  — prospect/company on the call
    call_date         date  — date of the call
    call_type         text  — e.g. 'Strategy call', 'Audit', 'Discovery'
    fireflies_url     text  — original Fireflies recording URL
    notes             text  — free-form notes from the source sheet
    transcript_id     text  — Fireflies transcript ID (unique)
    transcript_status text  — 'ok' or 'no_access (...)' if fetch failed
    category          text  — high-level call category, e.g.
                              'Discovery/Strategy Call', 'Discovery → Audit',
                              'Re-engagement', 'Partnership/Referral',
                              'Discovery → Pause/Decline'
    one_liner         text  — single sentence of what the call was about
    angle             text  — the pitch/strategy angle of the conversation
    sub_categories    jsonb — array of tags, e.g.
                              ["Meta ads", "CAC reduction", "Audit"]
    specialty         text  — brand vertical, e.g. 'DTC Beauty / Skincare',
                              'DTC Supplements (UK + DE)', 'Multi-brand DTC'
    pain_point        text  — the prospect's stated pain point
    transcript_md     text  — full Markdown transcript (header + summary +
                              action items + chronological dialogue)
    created_at        timestamptz

When categorization columns are empty, the transcript was inaccessible (workspace
permission). Filter `transcript_status = 'ok'` to skip those.

================================================================================
CLI USAGE
================================================================================
    # Defaults: client=kynship, status=ok, only metadata (no transcript)
    python tools/calls_db.py list

    # Filter by category / specialty / pain-point keyword
    python tools/calls_db.py list --category "Discovery → Audit"
    python tools/calls_db.py list --specialty-contains "Beauty"
    python tools/calls_db.py list --pain-contains "CAC"

    # Sub-category tag filter (jsonb @> on the array)
    python tools/calls_db.py list --tag "Meta ads" --tag "CAC reduction"

    # Full-text search inside transcript_md
    python tools/calls_db.py search "cost cap"
    python tools/calls_db.py search "ROAS" --client kynship

    # Pull one full record (including the transcript markdown)
    python tools/calls_db.py get --row-id 1
    python tools/calls_db.py get --company "BBQ Dripez"

    # Aggregations to scan a client's portfolio fast
    python tools/calls_db.py counts --by category
    python tools/calls_db.py counts --by specialty
    python tools/calls_db.py tags          # frequency of every sub_category tag

Output is JSON by default (`--format json`). Use `--format table` for terminal.

Env (from repo .env):
    SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

BASE = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
TABLE = "client_calls"

META_COLUMNS = (
    "id,row_id,client,company,call_date,call_type,fireflies_url,notes,"
    "transcript_id,transcript_status,category,one_liner,angle,sub_categories,"
    "specialty,pain_point,created_at"
)
ALL_COLUMNS = META_COLUMNS + ",transcript_md"


def _request(path: str, params: List[tuple]) -> Any:
    if not BASE or not KEY:
        sys.exit("Error: SUPABASE_URL / SUPABASE_PUBLISHABLE_KEY not set in .env")
    qs = urllib.parse.urlencode(params, doseq=True, safe="(),:.*")
    url = f"{BASE}/rest/v1/{path}?{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _build_filters(args) -> List[tuple]:
    p: List[tuple] = []
    if args.client:
        p.append(("client", f"eq.{args.client}"))
    if getattr(args, "status_ok", True):
        p.append(("transcript_status", "eq.ok"))
    if getattr(args, "category", None):
        p.append(("category", f"eq.{args.category}"))
    if getattr(args, "specialty_contains", None):
        p.append(("specialty", f"ilike.*{args.specialty_contains}*"))
    if getattr(args, "company_contains", None):
        p.append(("company", f"ilike.*{args.company_contains}*"))
    if getattr(args, "pain_contains", None):
        p.append(("pain_point", f"ilike.*{args.pain_contains}*"))
    if getattr(args, "angle_contains", None):
        p.append(("angle", f"ilike.*{args.angle_contains}*"))
    for tag in getattr(args, "tag", None) or []:
        # jsonb contains: sub_categories @> '["tag"]'
        p.append(("sub_categories", f"cs.[\"{tag}\"]"))
    if getattr(args, "since", None):
        p.append(("call_date", f"gte.{args.since}"))
    if getattr(args, "until", None):
        p.append(("call_date", f"lte.{args.until}"))
    return p


def _print(rows, fmt: str, columns: Optional[List[str]] = None):
    if fmt == "json":
        print(json.dumps(rows, indent=2, default=str))
        return
    if not rows:
        print("(no rows)")
        return
    cols = columns or ["row_id", "company", "call_date", "category", "specialty"]
    widths = {c: max(len(c), max(len(str(r.get(c) or "")) for r in rows)) for c in cols}
    widths = {c: min(w, 45) for c, w in widths.items()}
    print(" | ".join(c.ljust(widths[c]) for c in cols))
    print("-+-".join("-" * widths[c] for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c) or "")[:widths[c]].ljust(widths[c]) for c in cols))


# --- commands ----------------------------------------------------------------

def cmd_list(args):
    params = _build_filters(args)
    cols = ALL_COLUMNS if args.full else META_COLUMNS
    params += [("select", cols), ("order", "call_date.asc"), ("limit", str(args.limit))]
    _print(_request(TABLE, params), args.format)


def cmd_search(args):
    params = _build_filters(args)
    # Postgres ilike on transcript_md (the table has no FTS index by default,
    # this still works fine for our scale).
    params.append(("transcript_md", f"ilike.*{args.query}*"))
    cols = ALL_COLUMNS if args.full else META_COLUMNS
    params += [("select", cols), ("order", "call_date.asc"), ("limit", str(args.limit))]
    rows = _request(TABLE, params)
    _print(rows, args.format)
    if args.format == "table":
        print(f"\n{len(rows)} match(es) for {args.query!r}")


def cmd_get(args):
    params: List[tuple] = [("client", f"eq.{args.client}")]
    if args.row_id is not None:
        params.append(("row_id", f"eq.{args.row_id}"))
    elif args.company:
        params.append(("company", f"ilike.*{args.company}*"))
    elif args.transcript_id:
        params.append(("transcript_id", f"eq.{args.transcript_id}"))
    else:
        sys.exit("Error: provide --row-id, --company, or --transcript-id")
    params += [("select", ALL_COLUMNS), ("limit", "5")]
    rows = _request(TABLE, params)
    if not rows:
        sys.exit("No matching call found.")
    if args.format == "json":
        print(json.dumps(rows[0] if len(rows) == 1 else rows, indent=2, default=str))
        return
    for r in rows:
        print(f"\n{'=' * 78}")
        print(f"  Row {r['row_id']}: {r['company']} ({r['call_date']})  —  {r['category']}")
        print(f"  Specialty:  {r['specialty']}")
        print(f"  One-liner:  {r['one_liner']}")
        print(f"  Angle:      {r['angle']}")
        print(f"  Pain point: {r['pain_point']}")
        print(f"  Tags:       {', '.join(r.get('sub_categories') or [])}")
        print(f"  Fireflies:  {r['fireflies_url']}")
        print(f"{'=' * 78}\n")
        if args.transcript:
            print(r.get("transcript_md") or "(no transcript)")


def cmd_counts(args):
    params = [("client", f"eq.{args.client}"), ("transcript_status", "eq.ok"),
              ("select", args.by), ("limit", "10000")]
    rows = _request(TABLE, params)
    counter = Counter((r.get(args.by) or "(none)") for r in rows)
    for k, v in counter.most_common():
        print(f"{v:>4}  {k}")


def cmd_tags(args):
    params = [("client", f"eq.{args.client}"), ("transcript_status", "eq.ok"),
              ("select", "sub_categories"), ("limit", "10000")]
    rows = _request(TABLE, params)
    counter: Counter = Counter()
    for r in rows:
        for tag in r.get("sub_categories") or []:
            counter[tag] += 1
    for tag, n in counter.most_common():
        print(f"{n:>4}  {tag}")


# --- argparse ----------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Query the client_calls table in Supabase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--client", default="kynship", help="client filter (default: kynship)")
    p.add_argument("--format", choices=("json", "table"), default="table")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_filters(sp):
        sp.add_argument("--category")
        sp.add_argument("--specialty-contains")
        sp.add_argument("--company-contains")
        sp.add_argument("--pain-contains")
        sp.add_argument("--angle-contains")
        sp.add_argument("--tag", action="append", help="sub_categories tag (repeatable)")
        sp.add_argument("--since", help="YYYY-MM-DD, call_date >=")
        sp.add_argument("--until", help="YYYY-MM-DD, call_date <=")
        sp.add_argument("--include-no-access", dest="status_ok", action="store_false",
                        help="include rows whose transcript fetch failed")
        sp.add_argument("--limit", type=int, default=100)
        sp.add_argument("--full", action="store_true",
                        help="include transcript_md column (large)")

    sp = sub.add_parser("list", help="filter / list calls")
    add_filters(sp)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("search", help="full-text ilike on transcript_md")
    sp.add_argument("query")
    add_filters(sp)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("get", help="fetch one full call record")
    sp.add_argument("--row-id", type=int)
    sp.add_argument("--company")
    sp.add_argument("--transcript-id")
    sp.add_argument("--transcript", action="store_true",
                    help="also print the full transcript markdown")
    sp.set_defaults(func=cmd_get)

    sp = sub.add_parser("counts", help="group counts by a column")
    sp.add_argument("--by", default="category",
                    choices=("category", "specialty", "call_type", "transcript_status"))
    sp.set_defaults(func=cmd_counts)

    sp = sub.add_parser("tags", help="frequency of every sub_categories tag")
    sp.set_defaults(func=cmd_tags)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
