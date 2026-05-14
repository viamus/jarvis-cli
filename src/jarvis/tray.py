"""System tray integration for Jarvis daemon."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import pystray

from jarvis.icon import create_icon

if TYPE_CHECKING:
    from jarvis.daemon import Daemon


class TrayIcon:
    """Manages the Windows system tray icon for Jarvis."""

    def __init__(self, daemon: Daemon) -> None:
        self._daemon = daemon
        self._icon: pystray.Icon | None = None
        self._state = "idle"

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Jarvis Voice", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda _: f"Status: {self._state.capitalize()}",
                None,
                enabled=False,
            ),
            pystray.MenuItem(
                lambda _: f"Hotkey: {self._daemon._hotkey}",
                None,
                enabled=False,
            ),
            pystray.MenuItem(
                lambda _: f"Target: {self._target_label()}",
                None,
                enabled=False,
            ),
            pystray.MenuItem("Change Hotkey...", self._on_change_hotkey),
            pystray.MenuItem(
                "Target",
                pystray.Menu(
                    pystray.MenuItem("Claude Code (/jarvis)", self._on_target_claude),
                    pystray.MenuItem("Codex ($jarvis)", self._on_target_codex),
                ),
            ),
            pystray.MenuItem("System Info...", self._on_system_info),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    def _target_label(self) -> str:
        from jarvis.settings import get_target_command, get_target_label

        return f"{get_target_label(self._daemon._target)} ({get_target_command(self._daemon._target)})"

    def set_state(self, state: str) -> None:
        """Update icon state: 'idle', 'recording', or 'transcribing'."""
        self._state = state
        if self._icon is not None:
            self._icon.icon = create_icon(state)
            self._icon.title = f"Jarvis — {state.capitalize()}"

    def _on_change_hotkey(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Open the hotkey capture dialog."""
        from jarvis.hotkey_dialog import capture_hotkey
        from jarvis.settings import set_hotkey

        def _on_captured(new_hotkey: str) -> None:
            set_hotkey(new_hotkey)
            self._daemon.rebind_hotkey(new_hotkey)

        # Run dialog in a separate thread to not block the tray
        threading.Thread(target=capture_hotkey, args=(_on_captured,), daemon=True).start()

    def _set_target(self, target: str) -> None:
        self._daemon.set_target(target)
        if self._icon is not None:
            self._icon.update_menu()

    def _on_target_claude(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Select Claude Code as the auto-submit target."""
        self._set_target("claude")

    def _on_target_codex(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Select Codex as the auto-submit target."""
        self._set_target("codex")

    def _on_system_info(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Open the system info dialog."""
        from jarvis.info_dialog import show_info

        threading.Thread(target=show_info, args=(self._daemon,), daemon=True).start()

    def _on_quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._daemon.shutdown()
        icon.stop()

    def _setup(self, icon: pystray.Icon) -> None:
        """Called by pystray after the icon is created — makes it visible."""
        icon.visible = True

    def run(self) -> None:
        """Start the tray icon (blocks the calling thread)."""
        self._icon = pystray.Icon(
            name="jarvis",
            icon=create_icon("idle"),
            title="Jarvis — Idle",
            menu=self._build_menu(),
        )
        self._icon.run(setup=self._setup)

    def stop(self) -> None:
        """Stop the tray icon from another thread."""
        if self._icon is not None:
            self._icon.stop()
