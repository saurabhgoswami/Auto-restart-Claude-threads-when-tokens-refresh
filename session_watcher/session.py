from __future__ import annotations
import json
import time
from dataclasses import dataclass
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "sessions"
PROJECTS_DIR = Path.home() / ".claude" / "projects"
MAX_TITLE_LEN = 52


@dataclass
class ClaudeSession:
    session_id: str
    pid: int
    cwd: str
    started_at: int   # epoch ms
    version: str
    display_name: str  # derived from first message
    age_hours: float


def _cwd_to_project_key(cwd: str) -> str:
    """Convert /Users/foo/bar -> -Users-foo-bar (Claude's project dir encoding)."""
    return cwd.replace("/", "-")


def _read_first_message(session_id: str, cwd: str) -> str | None:
    """Return the first user message text from a session's JSONL file."""
    key = _cwd_to_project_key(cwd)
    jsonl_path = PROJECTS_DIR / key / f"{session_id}.jsonl"
    if not jsonl_path.exists():
        return None
    try:
        with jsonl_path.open() as fh:
            for line in fh:
                try:
                    d = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "user":
                    continue
                msg = d.get("message", {})
                content = msg.get("content", "")
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            content = part.get("text", "")
                            break
                if content and isinstance(content, str):
                    return content.strip()
    except OSError:
        pass
    return None


def _make_display_name(first_msg: str | None, session_id: str) -> str:
    if first_msg:
        # Collapse whitespace, truncate
        title = " ".join(first_msg.split())
        if len(title) > MAX_TITLE_LEN:
            title = title[:MAX_TITLE_LEN].rsplit(" ", 1)[0] + "…"
        return title
    return f"Session {session_id[:8]}"


def discover_sessions() -> list[ClaudeSession]:
    sessions: list[ClaudeSession] = []
    if not SESSIONS_DIR.exists():
        return sessions

    for path in SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        # Only surface desktop-app sessions
        if data.get("entrypoint", "") != "claude-desktop":
            continue

        session_id = data.get("sessionId", "")
        if not session_id:
            continue

        cwd = data.get("cwd") or data.get("workingDirectory", "")
        started_ms = data.get("startedAt") or data.get("startupTime", 0)
        age_h = (time.time() * 1000 - started_ms) / 3_600_000

        first_msg = _read_first_message(session_id, cwd)
        display_name = _make_display_name(first_msg, session_id)

        sessions.append(ClaudeSession(
            session_id=session_id,
            pid=data.get("pid", 0),
            cwd=cwd,
            started_at=started_ms,
            version=data.get("version", ""),
            display_name=display_name,
            age_hours=round(age_h, 1),
        ))

    return sorted(sessions, key=lambda s: s.started_at, reverse=True)
