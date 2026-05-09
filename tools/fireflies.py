"""
Fireflies.ai transcript fetcher.

Fetch a meeting transcript + summary from Fireflies and print it as readable
Markdown to stdout. Saving to disk is intentionally left to the caller — pipe
the output wherever you want it.

API docs: https://docs.fireflies.ai/graphql-api
Auth:     Bearer token (set FIREFLIES_API_KEY env var, or pass --api-key).

Usage:
    export FIREFLIES_API_KEY=xxxx
    python tools/fireflies.py "https://app.fireflies.ai/view/Some-Meeting::TRANSCRIPT_ID"
    python tools/fireflies.py "<url>" > meeting.md

Dependencies:
    pip install requests
"""

import argparse
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import requests

API_URL = "https://api.fireflies.ai/graphql"

QUERY = """query Transcript($transcriptId: String!) {
  transcript(id: $transcriptId) {
    id
    title
    dateString
    duration
    sentences { text speaker_name start_time end_time }
    summary { action_items keywords overview }
  }
}"""


def extract_transcript_id(url: str) -> Optional[str]:
    """Pull the transcript id that follows the `::` in a Fireflies URL."""
    m = re.search(r"::([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def fetch_transcript(transcript_id: str, api_key: str) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {"query": QUERY, "variables": {"transcriptId": transcript_id}}
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _fmt_time(seconds: Optional[float]) -> str:
    if seconds is None:
        return "00:00"
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def to_markdown(t: Dict[str, Any]) -> str:
    lines = []
    title = t.get("title") or "Untitled meeting"
    lines.append(f"# {title}")
    lines.append("")

    meta = []
    if t.get("dateString"):
        meta.append(f"**Date:** {t['dateString']}")
    if t.get("duration") is not None:
        meta.append(f"**Duration:** {t['duration']} min")
    if t.get("id"):
        meta.append(f"**Transcript ID:** `{t['id']}`")
    if meta:
        lines.append("  ".join(meta))
        lines.append("")

    summary = t.get("summary") or {}
    overview = summary.get("overview")
    if overview:
        lines.append("## Summary")
        lines.append("")
        lines.append(overview.strip())
        lines.append("")

    action_items = summary.get("action_items")
    if action_items:
        lines.append("## Action Items")
        lines.append("")
        if isinstance(action_items, list):
            for item in action_items:
                lines.append(f"- {item}")
        else:
            for raw in str(action_items).splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                lines.append(raw if raw.startswith(("-", "*")) else f"- {raw}")
        lines.append("")

    keywords = summary.get("keywords")
    if keywords:
        kws = keywords if isinstance(keywords, list) else [keywords]
        lines.append("## Keywords")
        lines.append("")
        lines.append(", ".join(str(k) for k in kws))
        lines.append("")

    sentences = t.get("sentences") or []
    if sentences:
        lines.append("## Transcript")
        lines.append("")
        sentences = sorted(sentences, key=lambda s: s.get("start_time") or 0)
        current_speaker = None
        for s in sentences:
            speaker = s.get("speaker_name") or "Unknown"
            ts = _fmt_time(s.get("start_time"))
            text = (s.get("text") or "").strip()
            if not text:
                continue
            if speaker != current_speaker:
                lines.append("")
                lines.append(f"**[{ts}] {speaker}:** {text}")
                current_speaker = speaker
            else:
                lines.append(f"**[{ts}]** {text}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a Fireflies meeting transcript and print it as Markdown."
    )
    parser.add_argument("url", help="Fireflies meeting URL (contains `::transcriptId`).")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("FIREFLIES_API_KEY"),
        help="Fireflies API key (defaults to FIREFLIES_API_KEY env var).",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: FIREFLIES_API_KEY env var is not set (or pass --api-key).", file=sys.stderr)
        return 2

    transcript_id = extract_transcript_id(args.url)
    if not transcript_id:
        print(
            "Error: could not extract transcriptId from URL. "
            "Expected the id to follow `::` in the URL.",
            file=sys.stderr,
        )
        return 2

    try:
        data = fetch_transcript(transcript_id, args.api_key)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status in (401, 403):
            print(
                f"Authorization error ({status}): the provided FIREFLIES_API_KEY does not "
                f"have workspace permission to access transcript {transcript_id}. "
                "Fireflies enforces workspace-level access — use a key from the workspace "
                "that owns this meeting.",
                file=sys.stderr,
            )
            return 3
        print(f"HTTP error {status}: {e}", file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        return 1

    if data.get("errors"):
        msg = "; ".join(err.get("message", "") for err in data["errors"])
        if any(k in msg.lower() for k in ("auth", "permission", "forbidden", "unauthorized")):
            print(
                f"Authorization error: {msg}. The API key lacks workspace permissions "
                f"for transcript {transcript_id}.",
                file=sys.stderr,
            )
            return 3
        print(f"GraphQL error: {msg}", file=sys.stderr)
        return 1

    transcript = (data.get("data") or {}).get("transcript")
    if not transcript:
        print(
            f"No transcript returned for {transcript_id}. This usually means the API key "
            "lacks workspace permissions for this specific meeting (Fireflies enforces "
            "workspace-level access). Try a key from the workspace that owns the meeting.",
            file=sys.stderr,
        )
        return 3

    sys.stdout.write(to_markdown(transcript))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
