from __future__ import annotations
import json
import time
from dataclasses import dataclass
from pathlib import Path

# Claude Code desktop stores sessions here with exact sidebar titles
_CLAUDE_APP_SESSIONS = (
    Path.home() / "Library" / "Application Support" / "Claude" / "claude-code-sessions"
)


@dataclass
class ClaudeSession:
    session_id: str    # cliSessionId — passed to `claude --resume`
    desktop_id: str    # local_XXXX — desktop app's own ID
    cwd: str
    title: str         # exact title shown in Claude Code sidebar
    age_hours: float
    is_archived: bool


def discover_sessions() -> list[ClaudeSession]:
    sessions: list[ClaudeSession] = []

    if not _CLAUDE_APP_SESSIONS.exists():
        return sessions

    for json_file in _CLAUDE_APP_SESSIONS.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        cli_session_id = data.get("cliSessionId", "")
        if not cli_session_id:
            continue

        is_archived = str(data.get("isArchived", "False")).lower() == "true"
        title = data.get("title", "").strip() or f"Session {cli_session_id[:8]}"

        last_activity_ms = int(data.get("lastActivityAt") or data.get("createdAt") or 0)
        age_h = (time.time() * 1000 - last_activity_ms) / 3_600_000

        sessions.append(ClaudeSession(
            session_id=cli_session_id,
            desktop_id=data.get("sessionId", ""),
            cwd=data.get("cwd", ""),
            title=title,
            age_hours=round(age_h, 1),
            is_archived=is_archived,
        ))

    # Sort newest activity first, archived last
    return sorted(sessions, key=lambda s: (s.is_archived, s.age_hours))
