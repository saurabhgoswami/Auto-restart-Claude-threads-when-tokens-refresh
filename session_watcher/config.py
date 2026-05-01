from __future__ import annotations
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "session-watcher"
STATE_PATH = CONFIG_DIR / "state.json"

DEFAULT_INTERVAL = 18000          # 5 hours in seconds
DEFAULT_PROMPT = "Continue from where you left off"
DEFAULT_TERMINAL_APP = "Terminal"
DEFAULT_CLAUDE_STARTUP_DELAY = 3  # seconds to wait for claude --resume to start
