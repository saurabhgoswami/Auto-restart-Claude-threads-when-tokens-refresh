from __future__ import annotations
import time

import rumps

from .session import ClaudeSession, discover_sessions
from .terminal import resume_session_in_terminal
from .watcher import WatcherState


class SessionWatcherApp(rumps.App):
    def __init__(self):
        super().__init__("Session Watcher", title="⏱ 0", quit_button=None)
        self.state = WatcherState.load()
        self._sessions: list[ClaudeSession] = []
        self._session_items: dict[str, rumps.MenuItem] = {}
        self._countdown_label = "Next restart in --:--:--"

        self._rebuild_menu()

        self._tick_timer = rumps.Timer(self._on_tick, 1)
        self._tick_timer.start()

        self._scan_timer = rumps.Timer(self._on_scan, 60)
        self._scan_timer.start()

    # ------------------------------------------------------------------ menu

    def _rebuild_menu(self):
        self._sessions = discover_sessions()
        self._session_items = {}

        items: list = []

        if self._sessions:
            for s in self._sessions:
                if s.is_archived:
                    continue
                is_watched = s.session_id in self.state.watched
                label = f"{'✓' if is_watched else '○'}  {s.title}  ({s.age_hours}h ago)"
                item = rumps.MenuItem(label, callback=self._toggle_session)
                item._session_id = s.session_id
                self._session_items[s.session_id] = item
                items.append(item)
        else:
            items.append(rumps.MenuItem("No Claude sessions found", callback=None))

        items += [
            rumps.separator,
            rumps.MenuItem(self._countdown_label),
            rumps.separator,
            rumps.MenuItem("Restart All Now", callback=self._restart_all),
            rumps.separator,
            rumps.MenuItem("Quit Session Watcher", callback=rumps.quit_application),
        ]

        self.menu.clear()
        self.menu = items

        watched_count = len(self.state.watched & {s.session_id for s in self._sessions})
        self.title = f"⏱ {watched_count}"

    # --------------------------------------------------------------- timers

    def _on_tick(self, _):
        self._update_countdown()
        self._check_due()

    def _on_scan(self, _):
        self._rebuild_menu()

    def _update_countdown(self):
        next_epoch = self.state.next_restart_epoch(self._sessions)
        remaining = max(0, int(next_epoch - time.time()))
        h, r = divmod(remaining, 3600)
        m, s = divmod(r, 60)
        new_label = f"Next restart in {h}:{m:02d}:{s:02d}"
        # Update title in-place via the stored label key
        try:
            self.menu[self._countdown_label].title = new_label
            self._countdown_label = new_label
        except KeyError:
            self._countdown_label = new_label

    def _check_due(self):
        for sid in self.state.sessions_due_now(self._sessions):
            self._do_restart(sid)

    # ------------------------------------------------------------ callbacks

    def _toggle_session(self, sender):
        sid = getattr(sender, "_session_id", None)
        if sid is None:
            return
        if sid in self.state.watched:
            self.state.watched.discard(sid)
        else:
            self.state.watched.add(sid)
        self.state.save()
        self._rebuild_menu()

    def _restart_all(self, _):
        for sid in list(self.state.watched):
            self._do_restart(sid)

    def _do_restart(self, session_id: str):
        # Find display name for notification
        name = next(
            (s.title for s in self._sessions if s.session_id == session_id),
            session_id[:8],
        )
        try:
            resume_session_in_terminal(
                session_id,
                self.state.continuation_prompt,
                self.state.claude_path,
                terminal_app=self.state.terminal_app,
                startup_delay=self.state.claude_startup_delay,
            )
            self.state.last_restart[session_id] = time.time()
            self.state.save()
            rumps.notification(
                title="Session Watcher",
                subtitle="Thread Resumed",
                message=name[:60],
            )
        except Exception as exc:
            rumps.notification(
                title="Session Watcher",
                subtitle="Restart Failed",
                message=str(exc),
            )
