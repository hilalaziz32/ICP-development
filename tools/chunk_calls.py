"""
chunk_calls.py — split call transcripts into topic-coherent chunks.

For every row in client_calls where transcript_status='ok' and no chunks exist
yet, send the dialogue portion of transcript_md to Claude, get back a JSON array
of chunks, and bulk-insert them into call_chunks.

A chunk = a contiguous block where one idea is being discussed (a pain, outcome,
objection, etc.). Target size: 3–15 utterances, ~100–400 words.

Env: SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY (or SERVICE_ROLE), ANTHROPIC_API_KEY
"""
import argparse
import json
import os
import re
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
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("CHUNKER_MODEL", "claude-sonnet-4-6")

SYSTEM = """You split a sales-call transcript into topic-coherent chunks for downstream retrieval.

The transcript will arrive with every dialogue line numbered like:
  L0001 [12:34] Speaker: text...
  L0002 [12:36] Speaker: text...

Rules:
- Each chunk is a contiguous range of line numbers where ONE coherent idea is discussed.
- Chunks must NOT overlap and together cover the whole transcript in order.
- Aim for 10–15 chunks total per call. Hard cap: 20.
- Each chunk should span ~5–25 lines.
- `label` is exactly one of: pain | ideal_outcome | current_solution | tried_failed | belief | objection | context
- `summary` is a single sentence (<=20 words) capturing the gist.

Return ONLY a JSON array, no prose. Schema per item:
{"start_line": 1, "end_line": 12, "label": "pain", "summary": "..."}

DO NOT include the verbatim text — only line numbers, label, summary."""


def sb_get(path, params):
    qs = urllib.parse.urlencode(params, doseq=True, safe="(),:.*")
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}?{qs}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def sb_patch(path, body):
    """PATCH expects ?filter in `path` (e.g. 'client_calls?id=eq.123')."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}",
        data=data,
        headers={
            "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def sb_post(path, rows):
    data = json.dumps(rows).encode()
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}",
        data=data,
        headers={
            "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode()


def claude_chunk(numbered_block: str) -> list:
    payload = {
        "model": MODEL,
        "max_tokens": 4000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": f"Numbered transcript:\n\n{numbered_block}\n\nReturn only the JSON array of {{start_line,end_line,label,summary}} objects."}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        body = json.loads(r.read().decode())
    text = "".join(b["text"] for b in body["content"] if b["type"] == "text").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    return json.loads(text)


_LINE_RE = re.compile(r"^\*?\*?\[(\d{1,2}:\d{2}(?::\d{2})?)\]\*?\*?\s*(?:\*?\*?([^:*]+?)\*?\*?:)?\s*(.*)$")


def parse_dialogue_lines(md: str) -> list[dict]:
    """Extract numbered dialogue lines from the '## Transcript' section.

    Returns list of {ts, speaker, text}. Handles fireflies output like:
        **[12:34] Speaker:** text
        **[12:36]** continuation by same speaker
    """
    i = md.find("## Transcript")
    body = md[i:] if i >= 0 else md
    out, current_speaker = [], None
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        ts, speaker, text = m.group(1), m.group(2), m.group(3).strip()
        if speaker:
            current_speaker = speaker.strip()
        if not text:
            continue
        out.append({"ts": ts, "speaker": current_speaker or "Unknown", "text": text})
    return out


def number_lines(lines: list[dict]) -> str:
    return "\n".join(
        f"L{i+1:04d} [{ln['ts']}] {ln['speaker']}: {ln['text']}"
        for i, ln in enumerate(lines)
    )


def reconstruct_chunk(lines: list[dict], start: int, end: int) -> dict:
    """Slice numbered lines [start..end] (1-indexed inclusive) into a chunk record."""
    sl = max(1, start) - 1
    el = min(len(lines), end)
    span = lines[sl:el]
    speakers = sorted({ln["speaker"] for ln in span})
    text = "\n".join(f"[{ln['ts']}] {ln['speaker']}: {ln['text']}" for ln in span)
    return {
        "start_time": span[0]["ts"] if span else None,
        "end_time": span[-1]["ts"] if span else None,
        "speakers": speakers,
        "text": text,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client", default="kynship")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--row-id", type=int, help="chunk a single row only")
    p.add_argument("--force", action="store_true", help="re-chunk even if chunks exist")
    args = p.parse_args()

    # Pull candidate calls. By default: not yet chunked.
    params = [("client", f"eq.{args.client}"), ("transcript_status", "eq.ok"),
              ("select", "id,row_id,client,company,transcript_md,"
                         "pain_point,angle,category,specialty,sub_categories"),
              ("order", "row_id.asc"), ("limit", str(args.limit))]
    if not args.force:
        params.append(("chunked", "eq.false"))
    if args.row_id is not None:
        params.append(("row_id", f"eq.{args.row_id}"))
    todo = sb_get("client_calls", params)
    print(f"{len(todo)} calls to chunk.")

    for c in todo:
        lines = parse_dialogue_lines(c["transcript_md"] or "")
        if len(lines) < 5:
            print(f"  row {c['row_id']} {c['company']}: dialogue too short ({len(lines)} lines), skip")
            continue
        numbered = number_lines(lines)
        t0 = time.time()
        print(f"  row {c['row_id']} {c['company']}: chunking ({len(lines)} lines, {len(numbered)} chars)...")
        try:
            spec = claude_chunk(numbered)
        except Exception as e:
            print(f"    ! chunk failed: {e}")
            continue
        rows = []
        for idx, ch in enumerate(spec):
            try:
                start, end = int(ch["start_line"]), int(ch["end_line"])
            except (KeyError, ValueError, TypeError):
                continue
            recon = reconstruct_chunk(lines, start, end)
            if not recon["text"]:
                continue
            label = ch.get("label") or "context"
            summary = ch.get("summary") or ""
            parent_pain = c.get("pain_point") or ""
            label_text_parts = [label, parent_pain, summary]
            label_text = " | ".join(p.strip() for p in label_text_parts if p and p.strip())
            rows.append({
                "call_id": c["id"],
                "client": c["client"],
                "chunk_idx": idx,
                "start_time": recon["start_time"],
                "end_time": recon["end_time"],
                "speakers": recon["speakers"],
                "text": recon["text"],
                "label": label,
                "summary": summary,
                "label_text": label_text,
                "parent_pain_point": c.get("pain_point"),
                "parent_angle": c.get("angle"),
                "parent_category": c.get("category"),
                "parent_specialty": c.get("specialty"),
                "parent_sub_categories": c.get("sub_categories"),
            })
        if args.force:
            # delete existing chunks for this call
            req = urllib.request.Request(
                f"{SB_URL}/rest/v1/call_chunks?call_id=eq.{c['id']}",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
                method="DELETE",
            )
            urllib.request.urlopen(req, timeout=30).read()
        # batch insert in groups of 50 to stay under request limits
        for i in range(0, len(rows), 50):
            sb_post("call_chunks", rows[i:i + 50])
        # flip the flag — embedded resets to false because new chunks have no vectors yet
        sb_patch(f"client_calls?id=eq.{c['id']}", {"chunked": True, "embedded": False})
        elapsed = time.time() - t0
        print(f"    inserted {len(rows)} chunks in {elapsed:.1f}s  (chunked=true)")
        time.sleep(0.4)

    print("Done.")


if __name__ == "__main__":
    main()
