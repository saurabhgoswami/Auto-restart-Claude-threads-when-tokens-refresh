<img src="assets/icon.svg" width="64" align="left" style="margin-right:16px"/>

# Auto-restart Claude threads when tokens refresh

> A macOS menu bar app that automatically resumes your Claude Code sessions the moment your token window refreshes — so your long-running AI tasks keep going without you babysitting them.

<br/>

---

## The problem

You set Claude Code to work on a big task — refactoring a codebase, generating a report, building a feature — and walk away. An hour later you come back and it's stalled. The context window ran out. You have to manually hunt down the session, open it, and tell it to continue.

This app fixes that.

---

## How it works

1. **Session Watcher** sits in your macOS menu bar as a `⏱` icon
2. It reads your active Claude Code sessions automatically
3. You click any session to **watch** it (toggle on/off)
4. Every **5 hours** (configurable), watched sessions are automatically resumed:
   - A Terminal window opens
   - `claude --resume <session-id>` is run
   - Your continuation prompt (`"Continue from where you left off"`) is sent automatically
5. A macOS notification confirms each restart

No cloud. No login. Runs entirely on your machine.

---

## Demo

```
⏱ 2   ← menu bar icon (2 sessions being watched)
│
├─ ✓  Build a full-stack swing trading system  (0.3h ago)
├─ ✓  Create a marketing operating system...   (4.1h ago)
├─ ○  Whenever I'm using Claude code, I alwa…  (19.8h ago)
│
├─ ───────────────────────────────────────
├─ Next restart in 4:32:11
├─ ───────────────────────────────────────
├─ Restart All Now
└─ Quit Session Watcher
```

---

## Requirements

| Requirement | Version |
|---|---|
| macOS | 12 Monterey or later |
| Python | 3.9+ (pre-installed on macOS) |
| Claude Code desktop app | Any recent version |
| Claude CLI (`claude`) | Required for full auto-resume |

---

## Installation

### 1. Install the Claude CLI (if you haven't)

```bash
npm install -g @anthropic-ai/claude-code
```

Verify it works:

```bash
claude --version
```

### 2. Clone this repo

```bash
git clone https://github.com/saurabhgoswami/Auto-restart-Claude-threads-when-tokens-refresh.git
cd Auto-restart-Claude-threads-when-tokens-refresh
```

### 3. Run the installer

```bash
bash install.sh
```

This will:
- Install the `rumps` Python dependency
- Register a **LaunchAgent** so the app starts automatically at every login
- Start the app immediately

Look for `⏱ 0` in your menu bar — you're live.

---

## Usage

### Watching a session

1. Open a Claude Code session and start your task
2. Click the `⏱` menu bar icon
3. Click the session name to toggle it on (✓ = being watched)
4. Walk away — Session Watcher will resume it every 5 hours automatically

### Manual restart

Click **"Restart All Now"** in the menu to immediately resume all watched sessions.

### Stopping the app

Click **"Quit Session Watcher"** in the menu. The LaunchAgent will restart it next login.

To uninstall permanently:

```bash
launchctl unload ~/Library/LaunchAgents/com.sessionwatcher.plist
rm ~/Library/LaunchAgents/com.sessionwatcher.plist
```

---

## Configuration

Edit `~/.config/session-watcher/state.json` to customize:

```json
{
  "interval_seconds": 18000,
  "continuation_prompt": "Continue from where you left off",
  "terminal_app": "Terminal",
  "claude_startup_delay": 3
}
```

| Key | Default | Description |
|---|---|---|
| `interval_seconds` | `18000` (5h) | How often to restart watched sessions |
| `continuation_prompt` | `"Continue from where you left off"` | Message sent to Claude on resume |
| `terminal_app` | `"Terminal"` | Use `"iTerm"` if you prefer iTerm2 |
| `claude_startup_delay` | `3` | Seconds to wait for `claude` to start before sending prompt |

Changes take effect on the next restart cycle — no need to relaunch the app.

---

## How sessions are named

Session Watcher reads the first message you sent in each Claude session to give it a meaningful name in the menu. Sessions are sorted newest-first.

---

## Troubleshooting

**`⏱` icon doesn't appear**

```bash
cd ~/Auto-restart-Claude-threads-when-tokens-refresh
python3 run.py
```

Check the error output. Common fix: `pip3 install rumps`

**Sessions show "No Claude sessions found"**

Make sure you have at least one session open in Claude Code desktop. Sessions are read from `~/.claude/sessions/`.

**Restart opens Terminal but doesn't type the prompt**

Increase the startup delay in your config:
```json
{ "claude_startup_delay": 6 }
```

**App crashes on startup**

Check the logs:
```bash
tail -f /tmp/session-watcher.err
```

**Claude CLI not found**

The app falls back to opening Claude.app and showing a notification if `claude` isn't on PATH. Install the CLI for full auto-resume:

```bash
npm install -g @anthropic-ai/claude-code
```

---

## Project structure

```
session-watcher/
├── session_watcher/
│   ├── app.py          # Menu bar UI and timer logic
│   ├── session.py      # Claude session discovery and naming
│   ├── watcher.py      # Watch state persistence and due-check
│   ├── terminal.py     # Terminal launcher via osascript
│   └── config.py       # Default constants
├── assets/
│   ├── icon.png        # Menu bar icon (22×22 template image)
│   └── icon.svg        # Logo for README and branding
├── run.py              # Entry point
├── install.sh          # One-command installer
├── com.sessionwatcher.plist  # LaunchAgent template
└── requirements.txt
```

---

## Contributing

Pull requests welcome. Key areas for improvement:

- Support for multiple Claude projects / working directories
- A preferences window for configuring interval and prompt
- Support for the Claude.ai web app (using browser extension)
- Windows / Linux support

---

## License

MIT — see [LICENSE](LICENSE)

---

Made for people who let Claude do the heavy lifting.
