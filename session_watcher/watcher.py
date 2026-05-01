from __future__ import annotations
import json
import os
import time
from pathlib import Path

from .config import (
    STATE_PATH,
    DEFAULT_INTERVAL,
    DEFAULT_PROMPT,
    DEFAULT_TERMINAL_APP,
    DEFAULT_CLAUDE_STARTUP_DELAY,
)
from .session import ClaudeSession


class WatcherState:
    def __init__(
        self,
        watched: set[str],
        last_restart: dict[str, float],
        interval_seconds: int,
        continuation_prompt: str,
        terminal_app: str,
        claude_startup_delay: int,
        claude_path: str | None,
    ):
        self.watched = watched
        self.last_restart = last_restart
        self.interval_seconds = interval_seconds
        self.continuation_prompt = continuation_prompt
        self.terminal_app = terminal_app
        self.claude_startup_delay = claude_startup_delay
        self.claude_path = claude_path

    @classmethod
    def load(cls) -> "WatcherState":
        from .terminal import find_claude
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(STATE_PATH.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        claude_path = find_claude()  # may be None if CLI not installed

        return cls(
            watched=set(data.get("watched", [])),
            last_restart=data.get("last_restart", {}),
            interval_seconds=data.get("interval_seconds", DEFAULT_INTERVAL),
            continuation_prompt=data.get("continuation_prompt", DEFAULT_PROMPT),
            terminal_app=data.get("terminal_app", DEFAULT_TERMINAL_APP),
            claude_startup_delay=data.get("claude_startup_delay", DEFAULT_CLAUDE_STARTUP_DELAY),
            claude_path=data.get("claude_path", claude_path),
        )

    def save(self):
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_PATH.with_suffix(".tmp")
        data = {
            "watched": list(self.watched),
            "last_restart": self.last_restart,
            "interval_seconds": self.interval_seconds,
            "continuation_prompt": self.continuation_prompt,
            "terminal_app": self.terminal_app,
            "claude_startup_delay": self.claude_startup_delay,
            "claude_path": self.claude_path,
        }
        tmp.write_text(json.dumps(data, indent=2))
        os.replace(tmp, STATE_PATH)

    def next_restart_epoch(self, sessions: list[ClaudeSession]) -> float:
        now = time.time()
        session_map = {s.session_id: s for s in sessions}
        earliest = now + self.interval_seconds

        for sid in self.watched:
            baseline = self.last_restart.get(sid)
            if baseline is None:
                s = session_map.get(sid)
                baseline = (s.started_at / 1000) if s else now
            due = baseline + self.interval_seconds
            if due < earliest:
                earliest = due

        return earliest

    def sessions_due_now(self, sessions: list[ClaudeSession]) -> list[str]:
        now = time.time()
        session_map = {s.session_id: s for s in sessions}
        due = []
        for sid in self.watched:
            baseline = self.last_restart.get(sid)
            if baseline is None:
                s = session_map.get(sid)
                baseline = (s.started_at / 1000) if s else now
            if now >= baseline + self.interval_seconds:
                due.append(sid)
        return due
