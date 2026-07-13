#!/usr/bin/env python3
"""Render a client's mined SMS copy history as a browsable page.

    python tools/sms_report.py --client leadgenix

Reads that client's output/ (written by tools/ghl_mine.py) and writes sms-copy-report.html.
T1+T2 render together because they ARE one unit — see .claude/skills/sms-performance.
"""
import argparse, csv, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(label, rows, totals, out_path):
    camps = sorted({r["campaign"] for r in rows})
    init = [r for r in rows if r["send"] == "initial"]
    tot_p = sum(r["prospects"] for r in init) or 1
    overall = round(100 * sum(r["replies"] for r in init) / tot_p, 2)
    esc = lambda s: html.escape(s or "")
    short = lambda c: esc(c.replace(f"{label} - ", "").replace(" | NA", ""))

    page = f"""<title>{esc(label)} — SMS copy that actually ran</title>
<style>
  :root {{
    --paper:#F4F5F7; --card:#FFF; --ink:#171A20; --ink-2:#3D4453; --muted:#6B7280;
    --line:#E1E4EA; --line-2:#EFF1F4; --accent:#B5771A; --accent-soft:#FBF0DC;
    --good:#1B7A4B; --bad:#B8413A; --bad-soft:#FAE7E5;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  }}
  @media (prefers-color-scheme:dark) {{ :root {{
    --paper:#0F1116; --card:#171A21; --ink:#E7E9ED; --ink-2:#B6BCC7; --muted:#818997;
    --line:#272C36; --line-2:#1E222A; --accent:#E0A84C; --accent-soft:#2E2617;
    --good:#4FBF85; --bad:#E2726A; --bad-soft:#341C1A; }} }}
  :root[data-theme="dark"] {{
    --paper:#0F1116; --card:#171A21; --ink:#E7E9ED; --ink-2:#B6BCC7; --muted:#818997;
    --line:#272C36; --line-2:#1E222A; --accent:#E0A84C; --accent-soft:#2E2617;
    --good:#4FBF85; --bad:#E2726A; --bad-soft:#341C1A; }}
  :root[data-theme="light"] {{
    --paper:#F4F5F7; --card:#FFF; --ink:#171A20; --ink-2:#3D4453; --muted:#6B7280;
    --line:#E1E4EA; --line-2:#EFF1F4; --accent:#B5771A; --accent-soft:#FBF0DC;
    --good:#1B7A4B; --bad:#B8413A; --bad-soft:#FAE7E5; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans);
    line-height:1.55; -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:0 24px 96px; }}
  header {{ padding:56px 0 26px; border-bottom:1px solid var(--line); }}
  .eyebrow {{ font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent);
    font-weight:650; margin:0 0 12px; }}
  h1 {{ font-family:var(--serif); font-size:clamp(30px,4.4vw,45px); line-height:1.12; margin:0 0 14px;
    font-weight:600; letter-spacing:-.01em; text-wrap:balance; }}
  .lede {{ max-width:68ch; color:var(--ink-2); margin:0; font-size:16px; }}
  .lede b {{ color:var(--ink); font-weight:600; }}
  .tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:1px;
    background:var(--line); border:1px solid var(--line); border-radius:7px; overflow:hidden; margin-top:28px; }}
  .tile {{ background:var(--card); padding:15px 18px; }}
  .tile .k {{ font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); font-weight:600; }}
  .tile .v {{ font-family:var(--serif); font-size:27px; font-weight:600; margin-top:3px; font-variant-numeric:tabular-nums; }}
  .tile.warn .v {{ color:var(--bad); }}
  .note {{ margin-top:24px; padding:14px 16px; background:var(--accent-soft); border-left:3px solid var(--accent);
    border-radius:0 7px 7px 0; font-size:14px; color:var(--ink-2); }}
  .note b {{ color:var(--ink); }}
  .bar {{ display:flex; flex-wrap:wrap; gap:9px; align-items:center; margin:30px 0 20px; }}
  select {{ appearance:none; background:var(--card); color:var(--ink); border:1px solid var(--line);
    border-radius:7px; padding:7px 30px 7px 11px; font:inherit; font-size:13px; cursor:pointer;
    background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);
    background-position:calc(100% - 16px) 14px,calc(100% - 11px) 14px; background-size:5px 5px; background-repeat:no-repeat; }}
  select:focus-visible {{ outline:2px solid var(--accent); outline-offset:1px; }}
  .hint {{ font-size:13px; color:var(--muted); margin-left:auto; }}
  .row {{ background:var(--card); border:1px solid var(--line); border-radius:7px; padding:16px 18px;
    margin-bottom:9px; display:grid; gap:14px; grid-template-columns:32px 1fr 218px; align-items:start; }}
  .row.burn {{ border-color:var(--bad); }}
  @media (max-width:840px) {{ .row {{ grid-template-columns:26px 1fr; }} .metrics {{ grid-column:2; }} }}
  .rank {{ font-family:var(--serif); font-size:19px; color:var(--muted); font-variant-numeric:tabular-nums; }}
  .row:first-of-type .rank {{ color:var(--accent); }}
  .txt {{ display:grid; grid-template-columns:26px 1fr; gap:9px; align-items:start; }}
  .txt + .txt {{ margin-top:9px; padding-top:9px; border-top:1px dashed var(--line); }}
  .leg {{ font-size:10px; font-weight:800; letter-spacing:.06em; color:var(--muted); padding-top:3px; }}
  .copy {{ font-family:var(--mono); font-size:13.5px; line-height:1.6; white-space:pre-wrap; word-break:break-word; }}
  .slot {{ color:var(--accent); background:var(--accent-soft); border-radius:3px; padding:0 3px; font-weight:600; }}
  .chars {{ font-size:11px; color:var(--muted); font-variant-numeric:tabular-nums; margin-top:3px; }}
  .meta {{ margin-top:11px; font-size:12px; color:var(--muted); display:flex; flex-wrap:wrap; gap:5px 8px; }}
  .tag {{ background:var(--line-2); border-radius:20px; padding:2px 9px; color:var(--ink-2); font-weight:500; }}
  .tag.rt {{ background:var(--accent-soft); color:var(--accent); font-weight:650; }}
  .metrics {{ display:flex; flex-direction:column; gap:9px; }}
  .m {{ display:grid; grid-template-columns:56px 1fr 50px; gap:8px; align-items:center; }}
  .m .lbl {{ color:var(--muted); font-weight:700; font-size:10px; letter-spacing:.05em; text-transform:uppercase; }}
  .track {{ height:6px; background:var(--line-2); border-radius:20px; overflow:hidden; }}
  .fill {{ height:100%; border-radius:20px; }}
  .fill.good {{ background:var(--good); }} .fill.bad {{ background:var(--bad); }}
  .num {{ font-variant-numeric:tabular-nums; font-weight:650; text-align:right; font-size:12.5px; }}
  .num.good {{ color:var(--good); }} .num.bad {{ color:var(--bad); }}
  .vol {{ font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; padding-top:4px;
    border-top:1px solid var(--line-2); }}
  .warnpill {{ display:inline-block; font-size:10.5px; font-weight:700; color:var(--bad); background:var(--bad-soft);
    border-radius:4px; padding:2px 7px; }}
  footer {{ margin-top:42px; padding-top:20px; border-top:1px solid var(--line); font-size:13px; color:var(--muted); }}
</style>

<div class="wrap">
<header>
  <p class="eyebrow">{esc(label)} · cold SMS</p>
  <h1>Every SMS you've actually run</h1>
  <p class="lede">You ship <b>two texts at once</b> — T1 and T2, seconds apart — so the pair is one piece of
  copy and is scored as one. Copy is edited <b>in place</b> inside GHL workflows, so a workflow only holds its
  <em>current</em> text; every variant you overwrote is gone from it. This is rebuilt from the send log — the
  only surviving record of what was really tested — with merge fields stripped back out against each contact's
  own values, leaving the <b>true structural copy</b>.</p>
  <div class="tiles">
    <div class="tile"><div class="k">Texts sent</div><div class="v">{totals['sent']:,}</div></div>
    <div class="tile"><div class="k">Prospects</div><div class="v">{totals['prospects']:,}</div></div>
    <div class="tile"><div class="k">Copy units</div><div class="v">{len(rows)}</div></div>
    <div class="tile"><div class="k">Campaigns</div><div class="v">{len(camps)}</div></div>
    <div class="tile"><div class="k">Reply rate</div><div class="v">{overall}%</div></div>
    <div class="tile warn"><div class="k">List-burners</div><div class="v">{totals['burners']}</div></div>
  </div>
  <p class="note"><b>Watch the opt-out bar, not just the reply bar.</b> A reply rate bought with an equal
  opt-out rate is a burned list, not a winner — those are outlined in red. <b>Retarget</b> sends are a second
  batch to the same prospect, weeks later.</p>
</header>

<div class="bar">
  <select id="send"><option value="initial">Initial send</option><option value="">Initial + retarget</option><option value="retarget">Retarget only</option></select>
  <select id="camp"><option value="">All campaigns</option>{"".join(f'<option value="{esc(c)}">{short(c)}</option>' for c in camps)}</select>
  <select id="sort"><option value="reply_pct">Best reply rate</option><option value="optout_pct">Worst opt-out</option><option value="prospects">Most sent</option></select>
  <select id="min"><option value="20">20+ prospects</option><option value="100" selected>100+</option><option value="300">300+</option></select>
  <span class="hint" id="hint"></span>
</div>
<div id="list"></div>
<footer>Rebuilt from GoHighLevel conversation logs · a reply is a genuine human reply; STOP / unsubscribe is
counted separately as an opt-out · generated by <code>tools/ghl_mine.py</code>.</footer>
</div>

<script>
const DATA = {json.dumps(rows)}, LABEL = {json.dumps(label)};
const $ = s => document.querySelector(s);
const slots = t => (t||"").replace(/[&<>]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;"}}[c]))
  .replace(/\\{{\\{{(\\w+)\\}}\\}}/g, '<span class="slot">{{{{$1}}}}</span>');
const camp = c => c.replace(LABEL + " - ", "").replace(" | NA", "");

function render() {{
  const sd = $("#send").value, c = $("#camp").value, s = $("#sort").value, mn = +$("#min").value;
  let rows = DATA.filter(r => (!sd || r.send.startsWith(sd)) && (!c || r.campaign === c) && r.prospects >= mn);
  rows.sort((a, b) => b[s] - a[s]);
  const maxR = Math.max(...rows.map(r => r.reply_pct), 1), maxO = Math.max(...rows.map(r => r.optout_pct), 1);
  $("#hint").textContent = rows.length
    ? `${{rows.length}} shown · ${{rows.reduce((n, r) => n + r.prospects, 0).toLocaleString()}} prospects`
    : "nothing matches — loosen the filters";
  $("#list").innerHTML = rows.map((r, i) => {{
    const t2 = r.T2 ? `<div class="txt"><span class="leg">T2</span><div><div class="copy">${{slots(r.T2)}}</div>
      <div class="chars">${{r.char_T2}} chars</div></div></div>` : "";
    const burn = r.burner ? `<div class="warnpill">opt-outs ≥ replies</div>` : "";
    const rt = r.send !== "initial" ? `<span class="tag rt">${{r.send}}</span>` : "";
    return `<article class="row ${{r.burner ? "burn" : ""}}">
      <div class="rank">${{i + 1}}</div>
      <div>
        <div class="txt"><span class="leg">T1</span><div><div class="copy">${{slots(r.T1)}}</div>
          <div class="chars">${{r.char_T1}} chars</div></div></div>
        ${{t2}}
        <div class="meta">${{rt}}<span class="tag">${{camp(r.campaign)}}</span>
          <span class="tag">${{r.first_sent}} → ${{r.last_sent}}</span></div>
      </div>
      <div class="metrics">
        <div class="m"><span class="lbl">Reply</span>
          <div class="track"><div class="fill good" style="width:${{Math.min(100, r.reply_pct / maxR * 100)}}%"></div></div>
          <span class="num good">${{r.reply_pct}}%</span></div>
        <div class="m"><span class="lbl">Opt-out</span>
          <div class="track"><div class="fill bad" style="width:${{Math.min(100, r.optout_pct / maxO * 100)}}%"></div></div>
          <span class="num bad">${{r.optout_pct}}%</span></div>
        <div class="vol">${{r.prospects.toLocaleString()}} prospects · ${{r.replies}} replies</div>
        ${{burn}}
      </div>
    </article>`;
  }}).join("");
}}
["#send", "#camp", "#sort", "#min"].forEach(s => $(s).addEventListener("change", render));
render();
</script>
"""
    open(out_path, "w").write(page)
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    a = ap.parse_args()
    reg = {k: v for k, v in json.load(open(os.path.join(ROOT, "clients", "registry.json"))).items()
           if not k.startswith("_")}
    if a.client not in reg:
        sys.exit(f"'{a.client}' not in registry. Known: {', '.join(sorted(reg))}")
    cfg = reg[a.client]
    label = cfg.get("label", a.client)
    out_dir = os.path.join(ROOT, cfg.get("output", f"clients/{a.client}/output"))
    bj = os.path.join(out_dir, "batches.json")
    if not os.path.exists(bj):
        sys.exit(f"No batches.json in {out_dir} — run: python tools/ghl_mine.py --client {a.client}")

    rows = json.load(open(bj))
    allrows = list(csv.DictReader(open(os.path.join(out_dir, "sms-copy-history.csv"))))
    totals = {
        "sent": sum(int(r["prospects"]) * int(r["texts_in_batch"]) for r in allrows),
        "prospects": sum(int(r["prospects"]) for r in allrows if r["send"] == "initial"),
        "burners": sum(1 for r in rows if r.get("burner")),
    }
    out_path = os.path.join(out_dir, "sms-copy-report.html")
    build(label, rows, totals, out_path)
    print(f"wrote {out_path}")
    print(f"  {len(rows)} copy units · {totals['prospects']:,} prospects · {totals['burners']} list-burners")


if __name__ == "__main__":
    main()
