"""
embed_chunks.py — fill `call_chunks.embedding` using Gemini embeddings.

Model: gemini-embedding-001, output_dimensionality=1536, task_type=RETRIEVAL_DOCUMENT.
Run after chunk_calls.py. Idempotent — only embeds rows where embedding IS NULL.

Env: SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY (or SERVICE_ROLE), GEMINI_API_KEY
"""
import argparse
import json
import os
import sys
import time
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
MODEL = "gemini-embedding-001"
DIM = 1536
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:embedContent?key={GEMINI_KEY}"
BATCH_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:batchEmbedContents?key={GEMINI_KEY}"


def sb_get(path, params):
    qs = urllib.parse.urlencode(params, doseq=True, safe="(),:.*")
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}?{qs}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def sb_patch(table_with_filter, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{table_with_filter}",
        data=data,
        headers={
            "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def gemini_embed_batch(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Batch embed via batchEmbedContents (much faster than per-item)."""
    payload = {
        "requests": [
            {
                "model": f"models/{MODEL}",
                "content": {"parts": [{"text": t}]},
                "taskType": task_type,
                "outputDimensionality": DIM,
            }
            for t in texts
        ]
    }
    req = urllib.request.Request(
        BATCH_ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read().decode())
    return [e["values"] for e in body["embeddings"]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client", default=None, help="filter to one client (omit = all clients)")
    p.add_argument("--batch", type=int, default=20, help="chunks per Gemini request")
    p.add_argument("--limit", type=int, default=10000, help="max chunks this run")
    args = p.parse_args()

    # Pull chunks where ANY of the 6 embedding columns is missing.
    params = [
        ("or", "(embedding.is.null,summary_embedding.is.null,label_embedding.is.null,pain_point_embedding.is.null,angle_embedding.is.null,sub_categories_embedding.is.null)"),
        ("select",
         "id,call_id,text,summary,label,label_text,parent_pain_point,parent_angle,parent_sub_categories,"
         "embedding,summary_embedding,label_embedding,pain_point_embedding,angle_embedding,sub_categories_embedding"),
        ("order", "id.asc"),
        ("limit", str(args.limit)),
    ]
    if args.client:
        params.append(("client", f"eq.{args.client}"))
    rows = sb_get("call_chunks", params)
    print(f"{len(rows)} chunks need embedding work.")

    def subcats_to_text(v):
        if v is None: return None
        if isinstance(v, list): return " | ".join(str(x) for x in v) or None
        return str(v) or None

    touched_calls = set()
    done = 0
    for i in range(0, len(rows), args.batch):
        batch = rows[i:i + args.batch]

        jobs = []  # (chunk_id, column, text_to_embed)
        for r in batch:
            if r.get("embedding") is None and r.get("text"):
                jobs.append((r["id"], "embedding", r["text"]))
            if r.get("summary_embedding") is None and r.get("summary"):
                jobs.append((r["id"], "summary_embedding", r["summary"]))
            if r.get("label_embedding") is None and (r.get("label_text") or r.get("label")):
                jobs.append((r["id"], "label_embedding", r.get("label_text") or r["label"]))
            if r.get("pain_point_embedding") is None and r.get("parent_pain_point"):
                jobs.append((r["id"], "pain_point_embedding", r["parent_pain_point"]))
            if r.get("angle_embedding") is None and r.get("parent_angle"):
                jobs.append((r["id"], "angle_embedding", r["parent_angle"]))
            sc_text = subcats_to_text(r.get("parent_sub_categories"))
            if r.get("sub_categories_embedding") is None and sc_text:
                jobs.append((r["id"], "sub_categories_embedding", sc_text))

        if not jobs:
            done += len(batch)
            continue

        try:
            vecs = gemini_embed_batch([j[2] for j in jobs])
        except urllib.error.HTTPError as e:
            print(f"  ! batch {i} failed: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
            time.sleep(2)
            continue

        # group updates per chunk to do one PATCH per chunk
        per_chunk = {}
        for (cid, col, _), v in zip(jobs, vecs):
            per_chunk.setdefault(cid, {})[col] = v
        for chunk_id, body in per_chunk.items():
            sb_patch(f"call_chunks?id=eq.{chunk_id}", body)
        for r in batch:
            touched_calls.add(r["call_id"])

        done += len(batch)
        print(f"  embedded {done}/{len(rows)} chunks ({len(jobs)} vectors this batch)")
        time.sleep(0.2)

    # Flip embedded=true once every embedding column is populated for the call.
    for cid in touched_calls:
        remaining = sb_get("call_chunks", [
            ("call_id", f"eq.{cid}"),
            ("or", "(embedding.is.null,summary_embedding.is.null,label_embedding.is.null,"
                    "pain_point_embedding.is.null,angle_embedding.is.null,sub_categories_embedding.is.null)"),
            ("select", "id"), ("limit", "1"),
        ])
        if not remaining:
            sb_patch(f"client_calls?id=eq.{cid}", {"embedded": True})

    print("Done.")


if __name__ == "__main__":
    main()
