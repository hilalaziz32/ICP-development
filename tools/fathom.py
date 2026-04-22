"""
Fathom.video API client.

Fetch meetings, transcripts, summaries, action items, and CRM matches from
Fathom and optionally save them to disk as readable Markdown.

API docs: https://developers.fathom.ai
Auth:     X-Api-Key header (set FATHOM_API_KEY env var, or pass api_key=).
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

BASE_URL = "https://api.fathom.ai/external/v1"


# ---------------------------------------------------------------------------
# low-level helpers
# ---------------------------------------------------------------------------

def _headers(api_key: Optional[str]) -> Dict[str, str]:
    key = api_key or os.environ.get("FATHOM_API_KEY")
    if not key:
        raise ValueError(
            "Fathom API key required. Set FATHOM_API_KEY env var or pass api_key=."
        )
    return {"X-Api-Key": key, "Accept": "application/json"}


def _extract_url_token(url: str) -> Optional[str]:
    """Pull the share/call token out of a fathom.video URL."""
    m = re.search(r"fathom\.video/(?:share/|calls/|call/)?([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def _parse_input(meeting_input: Union[str, int]) -> Dict[str, Any]:
    """Classify the user input as recording_id, url_token, or free-text query."""
    if isinstance(meeting_input, int):
        return {"type": "recording_id", "value": meeting_input}
    s = str(meeting_input).strip()
    if s.isdigit():
        return {"type": "recording_id", "value": int(s)}
    if "fathom.video" in s or s.startswith("http"):
        token = _extract_url_token(s)
        return {"type": "url_token", "value": token or s}
    return {"type": "query", "value": s}


# ---------------------------------------------------------------------------
# raw endpoints
# ---------------------------------------------------------------------------

def list_meetings(
    api_key: Optional[str] = None,
    cursor: Optional[str] = None,
    include_transcript: bool = False,
    include_summary: bool = False,
    include_action_items: bool = False,
    include_crm_matches: bool = False,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    recorded_by: Optional[Union[str, List[str]]] = None,
    teams: Optional[Union[str, List[str]]] = None,
) -> Dict[str, Any]:
    """GET /meetings — one page of meetings with optional filters + includes."""
    params: Dict[str, Any] = {}
    if cursor:
        params["cursor"] = cursor
    if include_transcript:
        params["include_transcript"] = "true"
    if include_summary:
        params["include_summary"] = "true"
    if include_action_items:
        params["include_action_items"] = "true"
    if include_crm_matches:
        params["include_crm_matches"] = "true"
    if created_after:
        params["created_after"] = created_after
    if created_before:
        params["created_before"] = created_before
    if recorded_by:
        params["recorded_by[]"] = (
            recorded_by if isinstance(recorded_by, list) else [recorded_by]
        )
    if teams:
        params["teams[]"] = teams if isinstance(teams, list) else [teams]

    resp = requests.get(f"{BASE_URL}/meetings", headers=_headers(api_key), params=params)
    resp.raise_for_status()
    return resp.json()


def iter_meetings(api_key: Optional[str] = None, **kwargs) -> Any:
    """Generator that pages through all meetings matching the given filters."""
    cursor = None
    while True:
        page = list_meetings(api_key=api_key, cursor=cursor, **kwargs)
        for item in page.get("items", []):
            yield item
        cursor = page.get("next_cursor")
        if not cursor:
            break


def get_transcript(recording_id: int, api_key: Optional[str] = None) -> Dict[str, Any]:
    """GET /recordings/{id}/transcript"""
    resp = requests.get(
        f"{BASE_URL}/recordings/{recording_id}/transcript",
        headers=_headers(api_key),
    )
    resp.raise_for_status()
    return resp.json()


def get_summary(recording_id: int, api_key: Optional[str] = None) -> Dict[str, Any]:
    """GET /recordings/{id}/summary"""
    resp = requests.get(
        f"{BASE_URL}/recordings/{recording_id}/summary",
        headers=_headers(api_key),
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------

def get_fathom_meeting(
    meeting_input: Union[str, int],
    save_path: Optional[str] = None,
    api_key: Optional[str] = None,
    include_transcript: bool = True,
    include_summary: bool = True,
    include_action_items: bool = True,
    include_crm_matches: bool = True,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch a single Fathom meeting with full details.

    `meeting_input` accepts any of:
      - int recording_id (e.g. 123456789)
      - numeric string ("123456789")
      - Fathom URL ("https://fathom.video/share/xyz" or "https://fathom.video/xyz")
      - free-text title query (matched case-insensitively against meeting titles)

    If `save_path` is provided, saves a readable `<name>.md` file. If
    `save_path` is a directory, a filename is auto-derived from the meeting
    title; otherwise the given path is used as the base.

    Narrow the search with `created_after` / `created_before` (ISO 8601) to
    speed up title/URL lookups across large accounts.

    Returns the meeting dict.
    """
    parsed = _parse_input(meeting_input)
    meeting = _find_meeting(
        parsed,
        api_key=api_key,
        include_transcript=include_transcript,
        include_summary=include_summary,
        include_action_items=include_action_items,
        include_crm_matches=include_crm_matches,
        created_after=created_after,
        created_before=created_before,
    )

    if meeting is None:
        raise ValueError(f"No Fathom meeting matched input: {meeting_input!r}")

    # backfill transcript/summary from dedicated endpoints if still missing
    rid = meeting.get("recording_id")
    if rid and include_transcript and not meeting.get("transcript"):
        try:
            meeting["transcript"] = get_transcript(rid, api_key=api_key).get(
                "transcript", []
            )
        except requests.HTTPError:
            pass
    if rid and include_summary and not meeting.get("default_summary"):
        try:
            meeting["default_summary"] = get_summary(rid, api_key=api_key).get("summary")
        except requests.HTTPError:
            pass

    if save_path:
        meeting["_saved_file"] = _save_meeting(meeting, save_path)

    return meeting


def export_meetings(
    save_dir: str,
    api_key: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    recorded_by: Optional[Union[str, List[str]]] = None,
    teams: Optional[Union[str, List[str]]] = None,
    include_transcript: bool = True,
    include_summary: bool = True,
    include_action_items: bool = True,
    include_crm_matches: bool = True,
) -> List[Dict[str, Any]]:
    """Bulk-export every meeting matching the filters into `save_dir` as Markdown."""
    saved = []
    for meeting in iter_meetings(
        api_key=api_key,
        include_transcript=include_transcript,
        include_summary=include_summary,
        include_action_items=include_action_items,
        include_crm_matches=include_crm_matches,
        created_after=created_after,
        created_before=created_before,
        recorded_by=recorded_by,
        teams=teams,
    ):
        md_path = _save_meeting(meeting, save_dir)
        saved.append(
            {"recording_id": meeting.get("recording_id"), "markdown": md_path}
        )
    return saved


# ---------------------------------------------------------------------------
# internals: lookup + persistence
# ---------------------------------------------------------------------------

def _find_meeting(
    parsed: Dict[str, Any],
    api_key: Optional[str],
    include_transcript: bool,
    include_summary: bool,
    include_action_items: bool,
    include_crm_matches: bool,
    created_after: Optional[str],
    created_before: Optional[str],
) -> Optional[Dict[str, Any]]:
    for m in iter_meetings(
        api_key=api_key,
        include_transcript=include_transcript,
        include_summary=include_summary,
        include_action_items=include_action_items,
        include_crm_matches=include_crm_matches,
        created_after=created_after,
        created_before=created_before,
    ):
        if parsed["type"] == "recording_id":
            if m.get("recording_id") == parsed["value"]:
                return m
        elif parsed["type"] == "url_token":
            val = parsed["value"] or ""
            if val and (
                val in (m.get("url") or "") or val in (m.get("share_url") or "")
            ):
                return m
        elif parsed["type"] == "query":
            q = parsed["value"].lower()
            if q in (m.get("meeting_title") or "").lower() or q in (
                m.get("title") or ""
            ).lower():
                return m
    return None


def _slug(text: Optional[str]) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:80] or "meeting"


def _save_meeting(meeting: Dict[str, Any], save_path: str) -> str:
    path = Path(save_path).expanduser()
    is_dir = path.suffix == "" or path.is_dir()

    if is_dir:
        path.mkdir(parents=True, exist_ok=True)
        base_name = _slug(
            meeting.get("meeting_title")
            or meeting.get("title")
            or f"meeting_{meeting.get('recording_id')}"
        )
        rid = meeting.get("recording_id")
        if rid:
            base_name = f"{base_name}_{rid}"
        md_path = path / f"{base_name}.md"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        md_path = path.with_suffix(".md")

    md_path.write_text(_to_markdown(meeting))
    return str(md_path)


def _to_markdown(m: Dict[str, Any]) -> str:
    lines: List[str] = []
    title = m.get("meeting_title") or m.get("title") or "Fathom Meeting"
    lines.append(f"# {title}\n")

    meta = []
    if m.get("scheduled_start_time"):
        meta.append(f"- **Scheduled:** {m['scheduled_start_time']}")
    if m.get("recording_start_time"):
        meta.append(f"- **Recorded:** {m['recording_start_time']}")
    rb = m.get("recorded_by") or {}
    if rb:
        meta.append(
            f"- **Recorded by:** {rb.get('name', '')} <{rb.get('email', '')}> "
            f"({rb.get('team', '')})"
        )
    if m.get("share_url"):
        meta.append(f"- **Share URL:** {m['share_url']}")
    elif m.get("url"):
        meta.append(f"- **URL:** {m['url']}")
    if m.get("recording_id"):
        meta.append(f"- **Recording ID:** {m['recording_id']}")
    if meta:
        lines.extend(meta)
        lines.append("")

    invitees = m.get("calendar_invitees") or []
    if invitees:
        lines.append("## Participants")
        for p in invitees:
            tag = " (external)" if p.get("is_external") else ""
            lines.append(f"- {p.get('name', '')} <{p.get('email', '')}>{tag}")
        lines.append("")

    summary = m.get("default_summary") or {}
    if summary.get("markdown_formatted"):
        lines.append("## Summary")
        lines.append(summary["markdown_formatted"].strip())
        lines.append("")

    actions = m.get("action_items") or []
    if actions:
        lines.append("## Action Items")
        for a in actions:
            assignee = (a.get("assignee") or {}).get("name") or "Unassigned"
            check = "[x]" if a.get("completed") else "[ ]"
            ts = a.get("recording_timestamp") or ""
            ts_part = f" _(at {ts})_" if ts else ""
            lines.append(
                f"- {check} **{assignee}** — {a.get('description', '')}{ts_part}"
            )
        lines.append("")

    crm = m.get("crm_matches") or {}
    if any(crm.get(k) for k in ("contacts", "companies", "deals")):
        lines.append("## CRM Matches")
        for c in crm.get("contacts") or []:
            lines.append(
                f"- **Contact:** {c.get('name', '')} <{c.get('email', '')}> — "
                f"{c.get('record_url', '')}"
            )
        for c in crm.get("companies") or []:
            lines.append(
                f"- **Company:** {c.get('name', '')} — {c.get('record_url', '')}"
            )
        for d in crm.get("deals") or []:
            amount = d.get("amount")
            amt = f" (${amount:,})" if isinstance(amount, (int, float)) else ""
            lines.append(
                f"- **Deal:** {d.get('name', '')}{amt} — {d.get('record_url', '')}"
            )
        lines.append("")

    transcript = m.get("transcript") or []
    if transcript:
        lines.append("## Transcript")
        for t in transcript:
            speaker = (t.get("speaker") or {}).get("display_name") or "Unknown"
            ts = t.get("timestamp", "")
            text = t.get("text", "")
            lines.append(f"**[{ts}] {speaker}:** {text}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Fetch a Fathom meeting by ID, URL, or title.")
    p.add_argument("input", help="Recording ID, Fathom URL, or title query")
    p.add_argument("-o", "--out", help="Path or directory to save Markdown")
    p.add_argument("--api-key", help="Fathom API key (or set FATHOM_API_KEY)")
    p.add_argument("--after", help="ISO 8601 created_after filter")
    p.add_argument("--before", help="ISO 8601 created_before filter")
    p.add_argument("--no-transcript", action="store_true")
    p.add_argument("--no-summary", action="store_true")
    p.add_argument("--no-actions", action="store_true")
    p.add_argument("--no-crm", action="store_true")
    args = p.parse_args()

    meeting = get_fathom_meeting(
        args.input,
        save_path=args.out,
        api_key=args.api_key,
        include_transcript=not args.no_transcript,
        include_summary=not args.no_summary,
        include_action_items=not args.no_actions,
        include_crm_matches=not args.no_crm,
        created_after=args.after,
        created_before=args.before,
    )

    saved = meeting.get("_saved_file")
    if saved:
        print(f"Saved: {saved}")
    else:
        print(_to_markdown(meeting))
