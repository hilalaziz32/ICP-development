"""
search_chunks_by_label.py — find every chunk of a given KIND (pain, outcome,
objection, etc.), then rank within that label by semantic relevance to a query.

WHEN TO USE THIS TOOL:
- You already know the bucket you want and need exhaustive coverage of it.
- The label is what matters; the query is just a way to sort within the bucket.
- Examples:
  * "Show me ALL pain points across the corpus."
  * "Pull every objection and rank by relevance to 'pricing'."
  * "I want every ideal_outcome chunk that's near 'profit margin growth'."

VALID LABELS:
  pain | ideal_outcome | current_solution | tried_failed | belief | objection | context

When to NOT use:
- You're doing free-form theme search → search_chunks_by_summary.py
- You want verbatim phrasing → search_chunks_by_text.py

Usage:
  # exhaustive list of every pain chunk:
  python3 tools/search_chunks_by_label.py pain --all [--client kynship]

  # pain chunks ranked by relevance to a query:
  python3 tools/search_chunks_by_label.py pain "high CAC" [--top 20]
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_PUBLISHABLE_KEY"]
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
DIM = 1536

VALID_LABELS = {"pain", "ideal_outcome", "current_solution", "tried_failed",
                "belief", "objection", "context"}


def embed_query(text: str) -> list[float]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_KEY}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_QUERY",
        "outputDimensionality": DIM,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["embedding"]["values"]


def list_all_for_label(label, client, limit=1000):
    params = [("label", f"eq.{label}"),
              ("select", "id,call_id,client,start_time,label,summary,text"),
              ("order", "id.asc"), ("limit", str(limit))]
    if client:
        params.append(("client", f"eq.{client}"))
    qs = urllib.parse.urlencode(params, safe="(),:.*")
    req = urllib.request.Request(f"{SB_URL}/rest/v1/call_chunks?{qs}",
                                 headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def ranked_by_query(label, query_vec, client, top):
    url = f"{SB_URL}/rest/v1/rpc/search_call_chunks"
    payload = {
        "query_embedding": query_vec,
        "embedding_column": "summary_embedding",
        "match_client": client,
        "match_label": label,
        "match_count": top,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                                          "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("label", help=f"one of: {', '.join(sorted(VALID_LABELS))}")
    p.add_argument("query", nargs="?", default=None)
    p.add_argument("--client", default=None,
                   help="filter to one client (omit for cross-client search across the whole corpus)")
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--all", action="store_true", help="dump every chunk of this label, no ranking")
    args = p.parse_args()

    if args.label not in VALID_LABELS:
        print(f"Invalid label. Valid: {sorted(VALID_LABELS)}", file=sys.stderr)
        sys.exit(2)

    if args.all or not args.query:
        rows = list_all_for_label(args.label, args.client)
    else:
        vec = embed_query(args.query)
        rows = ranked_by_query(args.label, vec, args.client, args.top)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
