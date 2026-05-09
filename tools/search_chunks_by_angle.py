"""
search_chunks_by_angle.py — find chunks whose PARENT CALL was pitched on a
given strategic angle.

Searches against angle_embedding (the parent call's `angle` denormalised onto
every chunk).

WHEN TO USE THIS TOOL:
- You're crafting an angle/hook and want every chunk from any call that was
  pitched on a similar angle — gives you a pile of evidence for/against.
- Examples:
  * "Find calls pitched on 'cut CAC by 50%' angle."
  * "Pull chunks from calls where the angle was creative-volume scaling."

CROSS-CLIENT BY DEFAULT — omit --client unless user explicitly limits.

Usage:
  python3 tools/search_chunks_by_angle.py "cut CAC by 50%" [--client <name>] [--top 15]
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
    payload = {"query_embedding": vec, "embedding_column": "angle_embedding",
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
                   help="filter to one client (omit = cross-client)")
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args()
    print(json.dumps(search(embed_query(args.query), args.client, args.top), indent=2))


if __name__ == "__main__":
    main()
