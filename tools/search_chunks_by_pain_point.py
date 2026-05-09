"""
search_chunks_by_pain_point.py — find chunks whose PARENT CALL was strategically
about a given pain point.

This searches against pain_point_embedding (the parent call's pain_point
denormalised onto every chunk). It's a knowledge-graph hop: "give me chunks
from any call where the strategic pain was X."

WHEN TO USE THIS TOOL:
- You're working on copy/positioning for a pain point and want every chunk
  from any call that was *about* that pain point — even if the chunk itself is
  context, action items, or pricing talk.
- Examples:
  * "Find every chunk from calls focused on high CAC."
  * "Pull chunks from calls where the strategic pain was creative volume."

DO NOT USE THIS TOOL when:
- You want chunks where the PROSPECT is themselves describing a pain →
  use search_chunks_by_label.py pain "<query>" or search_chunks_by_text.py.

CROSS-CLIENT BY DEFAULT — omit --client unless user explicitly limits.

Usage:
  python3 tools/search_chunks_by_pain_point.py "high CAC" [--client <name>] [--top 15]
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_PUBLISHABLE_KEY"]
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
DIM = 1536


def embed_query(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_KEY}"
    payload = {"model": "models/gemini-embedding-001",
               "content": {"parts": [{"text": text}]},
               "taskType": "RETRIEVAL_QUERY",
               "outputDimensionality": DIM}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["embedding"]["values"]


def search(vec, client, top):
    url = f"{SB_URL}/rest/v1/rpc/search_call_chunks"
    payload = {"query_embedding": vec, "embedding_column": "pain_point_embedding",
               "match_client": client, "match_label": None, "match_count": top}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                                          "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--client", default=None,
                   help="filter to one client (omit = cross-client across the whole corpus)")
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args()
    print(json.dumps(search(embed_query(args.query), args.client, args.top), indent=2))


if __name__ == "__main__":
    main()
