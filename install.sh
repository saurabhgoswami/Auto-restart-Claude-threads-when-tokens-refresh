#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)
PLIST_DEST="$HOME/Library/LaunchAgents/com.sessionwatcher.plist"

echo "Installing Session Watcher..."

# Install Python dependency
pip3 install -q rumps

# Install claude CLI if not already available (enables full auto-resume)
if ! command -v claude &>/dev/null; then
    echo "Installing claude CLI (enables full auto-resume)..."
    npm install -g @anthropic-ai/claude-code 2>/dev/null || \
        echo "  Warning: could not install claude CLI. App will open Claude.app as fallback."
fi

# Write the plist with real paths substituted
sed \
  -e "s|PYTHON_PATH|$PYTHON|g" \
  -e "s|SCRIPT_PATH|$SCRIPT_DIR/run.py|g" \
  "$SCRIPT_DIR/com.sessionwatcher.plist" > "$PLIST_DEST"

echo "Plist written to $PLIST_DEST"

# Unload if already loaded (ignore errors)
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Load and start
launchctl load -w "$PLIST_DEST"

echo ""
echo "Session Watcher is now running and will auto-start at login."
echo "Look for the ⏱ icon in your menu bar."
echo ""
echo "Logs: tail -f /tmp/session-watcher.log"
echo "Errors: tail -f /tmp/session-watcher.err"
