"""
search_chunks_by_summary.py — semantic search across the ONE-LINE GIST of every
chunk.

WHEN TO USE THIS TOOL:
- You want a high-level themes/concepts match, not exact wording.
- You're scanning many calls fast — summaries are dense and noise-free.
- Best for trend/pattern questions across an industry or vertical.
- Examples:
  * "What concepts come up around forecasting on these calls?"
  * "Find chunks themed around channel diversification."
  * "Are prospects worried about creative volume? Show me theme matches."

DO NOT USE THIS TOOL when:
- You want the exact words/voice of the prospect → use search_chunks_by_text.py
- You want every chunk of a known type → use search_chunks_by_label.py

Usage:
  python3 tools/search_chunks_by_summary.py "channel diversification anxiety" \\
      [--client kynship] [--top 10] [--label pain]
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


def search(query_vec, client, top, label=None):
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
    p.add_argument("query")
    p.add_argument("--client", default=None,
                   help="filter to one client (omit for cross-client search across the whole corpus)")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--label", help="filter to a single label")
    args = p.parse_args()

    vec = embed_query(args.query)
    hits = search(vec, args.client, args.top, args.label)
    print(json.dumps(hits, indent=2))


if __name__ == "__main__":
    main()
