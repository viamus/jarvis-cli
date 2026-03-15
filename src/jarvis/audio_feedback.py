"""Audio feedback beeps for recording start/stop."""

from __future__ import annotations

import sys
import threading


def _beep_in_thread(frequency: int, duration: int, times: int = 1) -> None:
    """Play winsound.Beep in a background thread so it doesn't block."""
    def _play():
        import winsound
        for _ in range(times):
            winsound.Beep(frequency, duration)

    threading.Thread(target=_play, daemon=True).start()


def beep_start() -> None:
    """High-pitched beep indicating recording started."""
    if sys.platform == "win32":
        _beep_in_thread(1000, 200)
    else:
        print("\a", end="", flush=True)


def beep_stop() -> None:
    """Double low-pitched beep indicating recording stopped."""
    if sys.platform == "win32":
        _beep_in_thread(600, 200, times=2)
    else:
        print("\a", end="", flush=True)


def beep_ready() -> None:
    """Ascending beep indicating transcription is ready."""
    if sys.platform == "win32":
        def _play():
            import winsound
            winsound.Beep(800, 100)
            winsound.Beep(1200, 100)
        threading.Thread(target=_play, daemon=True).start()
    else:
        print("\a", end="", flush=True)
