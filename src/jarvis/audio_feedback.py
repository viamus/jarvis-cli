"""Audio feedback beeps for recording start/stop."""

from __future__ import annotations

import sys


def beep_start() -> None:
    """High-pitched beep indicating recording started."""
    if sys.platform == "win32":
        import winsound
        winsound.Beep(1000, 200)
    else:
        print("\a", end="", flush=True)


def beep_stop() -> None:
    """Double low-pitched beep indicating recording stopped."""
    if sys.platform == "win32":
        import winsound
        winsound.Beep(600, 200)
        winsound.Beep(600, 200)
    else:
        print("\a", end="", flush=True)
