# CORPUS-FIRST PROTOCOL

Every research skill in this playground MUST query the call corpus in Supabase
BEFORE doing any live web search. Real prospect language we already paid to
record beats anything Google returns.

## Where the corpus lives

- Supabase tables: `client_calls` (one row per call) and `call_chunks` (~10–15
  topic-coherent chunks per call, each with 6 Gemini embeddings).
- Today: 31 calls / 303 chunks (kynship). More clients will land here over time.

## How to search it

There are 5 retrieval CLIs in `tools/`. **Always omit `--client` unless the
operator explicitly says "only client X" — patterns travel across clients and
we want the cross-pollination signal.**

| CLI | When to use |
|---|---|
| `python3 tools/search_chunks_by_text.py "<query>" [--top N]` | You need verbatim quotes / actual prospect phrasing. |
| `python3 tools/search_chunks_by_summary.py "<query>" [--top N]` | You need theme/concept matches across many calls. |
| `python3 tools/search_chunks_by_label.py <label> "<query>" [--top N]` | You want a bucket — `pain`, `ideal_outcome`, `current_solution`, `tried_failed`, `belief`, `objection`, `context` — ranked by query. |
| `python3 tools/search_chunks_by_pain_point.py "<query>" [--top N]` | KG hop — every chunk from any call whose strategic pain matched. |
| `python3 tools/search_chunks_by_angle.py "<query>" [--top N]` | KG hop — every chunk from any call pitched on that strategic angle. |

Each returns JSON with: `client`, `call_id`, `company` via call_id lookup,
`label`, `summary`, `text` (verbatim), `parent_pain_point`, `parent_angle`,
`parent_specialty`, `similarity`. Treat similarity > 0.65 as meaningful.

## Required workflow inside any research skill

1. **Form 3–6 search probes** from the skill's input (client name, ICP,
   persona, hypothesised pains/outcomes/objections). Use the prospect's
   probable language, not marketing language.
2. **Run corpus searches first.** Mix tool types — usually one
   `by_pain_point`, one `by_label pain "<query>"`, one `by_text "<query>"`.
   Cross-client (no `--client` flag).
3. **Read the JSON.** Pull verbatim quotes, note which `client`/`company` they
   come from, capture `start_time` for citation.
4. **Then go to live web search** to fill gaps the corpus doesn't cover
   (community signals, public reviews, fresh trends < 12 months).
5. **In your output, label each finding's source:**
   - `[CORPUS: <client> / <company> / call_id <N> @ <ts>]` for corpus quotes
   - `[WEB: <url>]` for web finds
6. **Prefer corpus quotes when both sources agree.** They are higher fidelity
   because they came from real qualified prospects on a paid call, not
   anonymous forum posters.

## When the corpus has nothing

If a corpus search returns weak hits (top similarity < 0.55), say so explicitly
in the output:
> "Corpus signal weak for '<query>' — relying on web research for this finding."

Do not silently skip the corpus and pretend it didn't return anything.

## Why cross-client

Pain points, objections, ideal-outcome language, and angles travel across
verticals. A "high CAC" complaint from a kynship prospect (DTC paid social) is
usually echoed verbatim by a UNITZERO prospect (AI automation for SMB home
services). The strategist needs that signal — narrowing to one client kills it.

The only time to scope to one client is when the operator explicitly says
"only kynship calls" / "scope to client X" / "for kynship's book only".
"For kynship I'm targeting…" is **NOT** a scope instruction — it's just naming
who the output is for.
