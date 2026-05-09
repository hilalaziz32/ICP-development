"""Push rec_enriched.csv into Supabase client_calls table."""
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import urllib.request

# Load .env from repo root.
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

URL = f"{os.environ['SUPABASE_URL']}/rest/v1/client_calls"
KEY = os.environ["SUPABASE_PUBLISHABLE_KEY"]
CLIENT = os.environ.get("CLIENT_NAME", "kynship")

CSV_PATH = Path(__file__).resolve().parent / "rec_enriched.csv"


def parse_date(s: str):
    s = s.strip()
    if not s:
        return None
    # Handle the typo "3/11/82026" → "3/11/2026"
    parts = s.split("/")
    if len(parts) == 3 and len(parts[2]) > 4:
        parts[2] = parts[2][-4:]
        s = "/".join(parts)
    for fmt in ("%m/%d/%Y", "%-m/%-d/%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def main():
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            try:
                subs = json.loads(r["sub_categories"]) if r["sub_categories"] else []
            except json.JSONDecodeError:
                subs = []
            rows.append({
                "client": CLIENT,
                "row_id": int(r["row_id"]),
                "company": r["company"].strip(),
                "call_date": parse_date(r["date"]),
                "call_type": r["call_type"].strip() or None,
                "fireflies_url": r["fireflies_url"] or None,
                "notes": r["notes"] or None,
                "transcript_id": r["transcript_id"] or None,
                "transcript_status": r["transcript_status"] or None,
                "category": r["category"] or None,
                "one_liner": r["one_liner"] or None,
                "angle": r["angle"] or None,
                "sub_categories": subs,
                "specialty": r["specialty"] or None,
                "pain_point": r["pain_point"] or None,
                "transcript_md": r["transcript_md"] or None,
            })

    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    # Batch in chunks to keep request bodies sane (transcripts are big).
    BATCH = 5
    inserted = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        data = json.dumps(chunk).encode()
        req = urllib.request.Request(URL, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode()
                inserted += len(chunk)
                print(f"  batch {i//BATCH + 1}: inserted {len(chunk)} (total {inserted}/{len(rows)})")
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            print(f"  batch {i//BATCH + 1} FAILED ({e.code}): {err[:500]}", file=sys.stderr)
            sys.exit(1)

    print(f"\nDone. {inserted} rows inserted into client_calls.")


if __name__ == "__main__":
    main()
