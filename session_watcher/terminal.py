from __future__ import annotations
import shutil
import subprocess
from pathlib import Path


def find_claude() -> str | None:
    """Return path to the claude CLI binary, or None if not installed."""
    candidates = [
        str(Path.home() / ".local" / "bin" / "claude"),
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
        str(Path.home() / ".claude" / "local" / "claude"),
        str(Path.home() / ".nvm" / "versions" / "node" / "v20" / "bin" / "claude"),
        str(Path.home() / ".nvm" / "versions" / "node" / "v18" / "bin" / "claude"),
        "/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude",
        "/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return shutil.which("claude")


def resume_session_in_terminal(
    session_id: str,
    prompt: str,
    claude_path: str | None,
    terminal_app: str = "Terminal",
    startup_delay: int = 3,
):
    if claude_path:
        _resume_via_cli(session_id, prompt, claude_path, terminal_app, startup_delay)
    else:
        _resume_via_app(session_id)


def _resume_via_cli(
    session_id: str,
    prompt: str,
    claude_path: str,
    terminal_app: str,
    startup_delay: int,
):
    safe_id = session_id.replace('"', "").replace("\\", "")
    safe_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"')
    safe_claude = claude_path.replace("\\", "\\\\").replace('"', '\\"')

    script = f'''
tell application "{terminal_app}"
    activate
    set t to do script "{safe_claude} --resume {safe_id}"
    delay {startup_delay}
    do script "{safe_prompt}" in t
    delay 0.3
    do script "" in t
end tell
'''
    subprocess.run(["osascript", "-e", script], check=True)


def _resume_via_app(session_id: str):
    """Fallback: open Claude.app and show a notification with session ID."""
    subprocess.run(["open", "-a", "Claude"], check=False)
    # Show a dialog with instructions since we can't auto-type
    short_id = session_id[:8]
    script = f'''
display notification "Open session {short_id}… and type your continuation prompt" ¬
    with title "Session Watcher" subtitle "Claude opened — resume manually"
'''
    subprocess.run(["osascript", "-e", script], check=False)
