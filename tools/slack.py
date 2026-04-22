"""
Slack conversation exporter.

Pull messages, threads, and file attachments from a Slack channel (or DM) and
save them as readable Markdown + downloaded attachments under a client folder.

Auth:  set SLACK_BOT_TOKEN in .env (bot token, starts with `xoxb-`).
       Bot needs scopes: channels:history, groups:history, im:history,
       mpim:history, channels:read, groups:read, users:read, files:read.

Inputs are flexible — a channel ID (`C0123ABCD`), a `#channel-name`, or any
Slack archive URL (`https://foo.slack.com/archives/C0123ABCD/p1712345678000100`).
Filter by absolute dates (`--after 2026-01-01`), relative windows (`--days 14`),
or message count. Threads and files are fetched by default.

Example:
    python tools/slack.py "#kynship-ops" -o clients/kynship/slack --days 30
    python tools/slack.py https://scaletopia.slack.com/archives/C09ABC123 \\
        -o clients/kynship/slack --after 2026-03-01 --before 2026-04-01
"""

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import requests

try:
    from dotenv import load_dotenv  # optional
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

BASE_URL = "https://slack.com/api"


# ---------------------------------------------------------------------------
# low-level helpers
# ---------------------------------------------------------------------------

def _token(token: Optional[str]) -> str:
    t = token or os.environ.get("SLACK_BOT_TOKEN") or os.environ.get("slack_bot_token")
    if not t:
        raise ValueError(
            "Slack bot token required. Set SLACK_BOT_TOKEN in .env or pass token=."
        )
    return t


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _call(method: str, token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Slack Web API GET call with rate-limit retry."""
    for _ in range(5):
        resp = requests.get(
            f"{BASE_URL}/{method}", headers=_headers(token), params=params or {}
        )
        if resp.status_code == 429:
            retry = int(resp.headers.get("Retry-After", "2"))
            time.sleep(retry)
            continue
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error on {method}: {data.get('error')}")
        return data
    raise RuntimeError(f"Slack API rate-limit retries exhausted on {method}")


# ---------------------------------------------------------------------------
# input parsing / resolution
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"slack\.com/archives/([A-Z0-9]+)(?:/p(\d+))?")


def _parse_channel_input(channel_input: str) -> Dict[str, Optional[str]]:
    """Return {'id': ..., 'name': ..., 'thread_ts': ...} given any form of input."""
    s = channel_input.strip()
    m = _URL_RE.search(s)
    if m:
        cid = m.group(1)
        p = m.group(2)
        ts = None
        if p and len(p) >= 7:
            ts = f"{p[:-6]}.{p[-6:]}"  # p1712345678000100 -> 1712345678.000100
        return {"id": cid, "name": None, "thread_ts": ts}
    if re.fullmatch(r"[CDG][A-Z0-9]{5,}", s):
        return {"id": s, "name": None, "thread_ts": None}
    return {"id": None, "name": s.lstrip("#"), "thread_ts": None}


def _resolve_channel_id(name: str, token: str) -> Tuple[str, str]:
    """Look up a channel ID by name. Returns (id, display_name)."""
    cursor = None
    while True:
        params = {
            "limit": 1000,
            "types": "public_channel,private_channel,mpim,im",
            "exclude_archived": "false",
        }
        if cursor:
            params["cursor"] = cursor
        data = _call("conversations.list", token, params)
        for ch in data.get("channels", []):
            if ch.get("name") == name or ch.get("name_normalized") == name:
                return ch["id"], ch.get("name") or ch["id"]
        cursor = (data.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
    raise ValueError(f"Channel '#{name}' not found (bot may not be a member).")


def _parse_date(value: Optional[str]) -> Optional[float]:
    """Parse YYYY-MM-DD or ISO 8601 into a Unix timestamp (UTC)."""
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {value!r}")


# ---------------------------------------------------------------------------
# fetchers
# ---------------------------------------------------------------------------

def iter_history(
    channel_id: str,
    token: str,
    oldest: Optional[float] = None,
    latest: Optional[float] = None,
    limit: Optional[int] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield messages from conversations.history, oldest-first, with paging."""
    collected: List[Dict[str, Any]] = []
    cursor = None
    while True:
        params: Dict[str, Any] = {"channel": channel_id, "limit": 200}
        if oldest:
            params["oldest"] = oldest
        if latest:
            params["latest"] = latest
        if cursor:
            params["cursor"] = cursor
        data = _call("conversations.history", token, params)
        collected.extend(data.get("messages", []))
        cursor = (data.get("response_metadata") or {}).get("next_cursor")
        if not cursor or (limit and len(collected) >= limit):
            break
    # Slack returns newest-first; flip for readable transcripts.
    collected.sort(key=lambda m: float(m.get("ts", 0)))
    if limit:
        collected = collected[-limit:]
    for m in collected:
        yield m


def fetch_replies(channel_id: str, thread_ts: str, token: str) -> List[Dict[str, Any]]:
    """All messages in a thread (includes the root)."""
    out: List[Dict[str, Any]] = []
    cursor = None
    while True:
        params: Dict[str, Any] = {"channel": channel_id, "ts": thread_ts, "limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = _call("conversations.replies", token, params)
        out.extend(data.get("messages", []))
        cursor = (data.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
    out.sort(key=lambda m: float(m.get("ts", 0)))
    return out


class _UserCache:
    def __init__(self, token: str) -> None:
        self._token = token
        self._by_id: Dict[str, str] = {}

    def name(self, user_id: Optional[str]) -> str:
        if not user_id:
            return "unknown"
        if user_id in self._by_id:
            return self._by_id[user_id]
        try:
            data = _call("users.info", self._token, {"user": user_id})
            u = data.get("user") or {}
            profile = u.get("profile") or {}
            display = (
                profile.get("display_name")
                or profile.get("real_name")
                or u.get("real_name")
                or u.get("name")
                or user_id
            )
        except Exception:
            display = user_id
        self._by_id[user_id] = display
        return display


# ---------------------------------------------------------------------------
# attachments
# ---------------------------------------------------------------------------

def _download_file(
    file_obj: Dict[str, Any], dest_dir: Path, token: str
) -> Optional[str]:
    url = file_obj.get("url_private_download") or file_obj.get("url_private")
    if not url:
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    fid = file_obj.get("id") or "file"
    name = file_obj.get("name") or f"{fid}.bin"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    out_path = dest_dir / f"{fid}_{safe}"
    if out_path.exists():
        return str(out_path)
    try:
        r = requests.get(url, headers=_headers(token), stream=True, timeout=60)
        r.raise_for_status()
        with out_path.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    fh.write(chunk)
        return str(out_path)
    except requests.HTTPError:
        return None


# ---------------------------------------------------------------------------
# markdown rendering
# ---------------------------------------------------------------------------

_MENTION_RE = re.compile(r"<@([UW][A-Z0-9]+)(?:\|([^>]+))?>")
_CHANNEL_RE = re.compile(r"<#([CDG][A-Z0-9]+)(?:\|([^>]+))?>")
_LINK_RE = re.compile(r"<(https?://[^|>]+)(?:\|([^>]+))?>")


def _humanize(text: str, users: _UserCache) -> str:
    text = _MENTION_RE.sub(lambda m: f"@{m.group(2) or users.name(m.group(1))}", text)
    text = _CHANNEL_RE.sub(lambda m: f"#{m.group(2) or m.group(1)}", text)
    text = _LINK_RE.sub(lambda m: m.group(2) or m.group(1), text)
    return text


def _fmt_ts(ts: str) -> str:
    try:
        return (
            datetime.fromtimestamp(float(ts), tz=timezone.utc)
            .strftime("%Y-%m-%d %H:%M:%S UTC")
        )
    except (TypeError, ValueError):
        return ts


def _render_message(
    msg: Dict[str, Any],
    users: _UserCache,
    files_rel: Dict[str, str],
    indent: int = 0,
) -> List[str]:
    pad = "  " * indent
    author = users.name(msg.get("user") or msg.get("bot_id"))
    ts = _fmt_ts(msg.get("ts", ""))
    head = f"{pad}- **{author}** · _{ts}_"
    lines = [head]
    body = _humanize(msg.get("text") or "", users).strip()
    if body:
        for ln in body.splitlines():
            lines.append(f"{pad}  {ln}")
    for f in msg.get("files") or []:
        fid = f.get("id")
        label = f.get("name") or fid or "file"
        rel = files_rel.get(fid)
        if rel:
            lines.append(f"{pad}  - 📎 [{label}]({rel})")
        else:
            lines.append(f"{pad}  - 📎 {label} _(not downloaded)_")
    for att in msg.get("attachments") or []:
        txt = att.get("text") or att.get("fallback") or ""
        if txt:
            lines.append(f"{pad}  > {_humanize(txt, users).splitlines()[0]}")
    return lines


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------

def export_slack(
    channel_input: str,
    save_path: str,
    token: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    days: Optional[int] = None,
    limit: Optional[int] = None,
    include_threads: bool = True,
    include_files: bool = True,
) -> Dict[str, Any]:
    """
    Export a Slack channel's messages + attachments to `save_path`.

    `channel_input` accepts channel ID, `#channel-name`, or any archive URL
    (including a link to a specific message, which scopes the export to that
    single thread).

    Time filters stack: `days` sets `after = now - days`; explicit `after` /
    `before` (YYYY-MM-DD or ISO 8601) override. `limit` caps the most recent
    messages after filtering.

    Returns a summary dict with counts and output paths.
    """
    tok = _token(token)
    parsed = _parse_channel_input(channel_input)
    channel_id = parsed["id"]
    display = parsed["name"] or channel_id
    if not channel_id:
        channel_id, display = _resolve_channel_id(parsed["name"], tok)

    oldest = _parse_date(after)
    latest = _parse_date(before)
    if days and not oldest:
        oldest = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()

    out_dir = Path(save_path).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    files_dir = out_dir / "attachments"

    users = _UserCache(tok)

    # Single-thread export if URL pointed at a specific message.
    if parsed["thread_ts"]:
        thread_msgs = fetch_replies(channel_id, parsed["thread_ts"], tok)
        messages = thread_msgs
        top_level = [thread_msgs[0]] if thread_msgs else []
    else:
        top_level = list(iter_history(channel_id, tok, oldest, latest, limit))
        messages = list(top_level)
        if include_threads:
            for m in top_level:
                if m.get("thread_ts") and m.get("reply_count"):
                    replies = fetch_replies(channel_id, m["thread_ts"], tok)
                    # first element is the root (already in top_level)
                    messages.extend(replies[1:])

    # Download attachments; keep a map of file_id -> relative path for rendering.
    files_rel: Dict[str, str] = {}
    file_count = 0
    if include_files:
        seen: set = set()
        for m in messages:
            for f in m.get("files") or []:
                fid = f.get("id")
                if not fid or fid in seen:
                    continue
                seen.add(fid)
                saved = _download_file(f, files_dir, tok)
                if saved:
                    files_rel[fid] = os.path.relpath(saved, out_dir)
                    file_count += 1

    # Render markdown: top-level messages, with nested replies under each root.
    md_lines: List[str] = [
        f"# Slack export — #{display}",
        "",
        f"- **Channel ID:** {channel_id}",
    ]
    if oldest:
        md_lines.append(f"- **After:** {_fmt_ts(str(oldest))}")
    if latest:
        md_lines.append(f"- **Before:** {_fmt_ts(str(latest))}")
    md_lines.append(f"- **Messages:** {len(messages)}")
    md_lines.append(f"- **Attachments saved:** {file_count}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    replies_by_root: Dict[str, List[Dict[str, Any]]] = {}
    if not parsed["thread_ts"]:
        for m in messages:
            root = m.get("thread_ts")
            if root and root != m.get("ts"):
                replies_by_root.setdefault(root, []).append(m)

    if parsed["thread_ts"]:
        # Full thread dump
        for i, m in enumerate(messages):
            md_lines.extend(_render_message(m, users, files_rel, indent=0 if i == 0 else 1))
            md_lines.append("")
    else:
        for m in top_level:
            md_lines.extend(_render_message(m, users, files_rel, indent=0))
            for r in replies_by_root.get(m.get("ts") or "", []):
                md_lines.extend(_render_message(r, users, files_rel, indent=1))
            md_lines.append("")

    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", display).strip("-") or channel_id
    md_path = out_dir / f"slack_{slug}.md"
    json_path = out_dir / f"slack_{slug}.json"
    md_path.write_text("\n".join(md_lines))
    json_path.write_text(json.dumps(messages, indent=2, sort_keys=True))

    return {
        "channel_id": channel_id,
        "channel_name": display,
        "message_count": len(messages),
        "file_count": file_count,
        "markdown": str(md_path),
        "json": str(json_path),
        "attachments_dir": str(files_dir) if file_count else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Export a Slack channel to Markdown + files.")
    p.add_argument("channel", help="Channel ID, #name, or archive URL")
    p.add_argument("-o", "--out", required=True, help="Output directory (e.g. clients/foo/slack)")
    p.add_argument("--token", help="Slack bot token (or set SLACK_BOT_TOKEN)")
    p.add_argument("--after", help="Oldest date (YYYY-MM-DD or ISO 8601)")
    p.add_argument("--before", help="Newest date (YYYY-MM-DD or ISO 8601)")
    p.add_argument("--days", type=int, help="Shortcut: last N days")
    p.add_argument("--limit", type=int, help="Max top-level messages")
    p.add_argument("--no-threads", action="store_true", help="Skip fetching thread replies")
    p.add_argument("--no-files", action="store_true", help="Skip downloading attachments")
    args = p.parse_args()

    result = export_slack(
        args.channel,
        save_path=args.out,
        token=args.token,
        after=args.after,
        before=args.before,
        days=args.days,
        limit=args.limit,
        include_threads=not args.no_threads,
        include_files=not args.no_files,
    )
    print(json.dumps(result, indent=2))
