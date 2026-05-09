"""One-off: fetch all Fireflies transcripts referenced in rec.csv and save to disk."""
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from fireflies import extract_transcript_id, fetch_transcript, to_markdown  # noqa: E402

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "rec.csv"
OUT_DIR = ROOT / "transcripts"
OUT_DIR.mkdir(exist_ok=True)
INDEX = ROOT / "transcripts_index.json"

ENV_PATH = ROOT.parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ["FIREFLIES_API_KEY"]

rows = []
with SRC.open() as f:
    for line in f:
        parts = [p.strip() for p in line.rstrip("\n").split("\t") if p.strip()]
        if len(parts) < 4:
            continue
        company, date, call_type, url = parts[0], parts[1], parts[2], parts[3]
        notes = parts[4] if len(parts) > 4 else ""
        rows.append({"company": company, "date": date, "type": call_type, "url": url, "notes": notes})

index = []
for i, r in enumerate(rows, 1):
    tid = extract_transcript_id(r["url"])
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", r["company"]).strip("_")
    md_path = OUT_DIR / f"{i:02d}_{safe}_{tid}.md"
    status = "ok"
    err = ""
    try:
        if md_path.exists() and md_path.stat().st_size > 500:
            print(f"[{i}/{len(rows)}] cached {r['company']}")
        else:
            print(f"[{i}/{len(rows)}] fetching {r['company']} ({tid})")
            data = fetch_transcript(tid, API_KEY)
            if data.get("errors"):
                status = "error"
                err = "; ".join(e.get("message", "") for e in data["errors"])
            else:
                t = (data.get("data") or {}).get("transcript")
                if not t:
                    status = "no_access"
                    err = "null transcript (workspace permission)"
                else:
                    md_path.write_text(to_markdown(t))
        time.sleep(0.4)
    except Exception as e:
        status = "exception"
        err = str(e)
        print(f"  ! {err}")
    index.append({**r, "transcript_id": tid, "file": str(md_path.relative_to(ROOT)), "status": status, "error": err})

INDEX.write_text(json.dumps(index, indent=2))
print(f"\nDone. Index: {INDEX}")
print(f"OK: {sum(1 for x in index if x['status']=='ok')} / {len(index)}")
