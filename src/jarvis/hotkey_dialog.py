"""Hotkey capture dialog using tkinter."""

from __future__ import annotations

import tkinter as tk
from typing import Callable


def capture_hotkey(on_captured: Callable[[str], None]) -> None:
    """Open a dialog that captures a key combination and calls on_captured(hotkey_str).

    Runs in its own thread-safe tkinter mainloop.
    """
    root = tk.Tk()
    root.title("Jarvis — Configure Hotkey")
    root.geometry("360x160")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # Center on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 360) // 2
    y = (root.winfo_screenheight() - 160) // 2
    root.geometry(f"+{x}+{y}")

    label = tk.Label(
        root,
        text="Press the desired key combination\n(e.g. Ctrl+Alt+J, F5, etc.)",
        font=("Segoe UI", 11),
        pady=10,
    )
    label.pack()

    captured_label = tk.Label(
        root,
        text="Waiting...",
        font=("Segoe UI", 14, "bold"),
        fg="#0088aa",
        pady=5,
    )
    captured_label.pack()

    captured_hotkey: list[str | None] = [None]

    def _on_key(event: tk.Event) -> str:
        parts = []
        if event.state & 0x4:
            parts.append("ctrl")
        if event.state & 0x8:
            parts.append("alt")
        if event.state & 0x1:
            parts.append("shift")

        key = event.keysym.lower()
        # Skip modifier-only presses
        if key in ("control_l", "control_r", "alt_l", "alt_r", "shift_l", "shift_r"):
            return "break"

        parts.append(key)
        hotkey = "+".join(parts)
        captured_hotkey[0] = hotkey
        captured_label.config(text=hotkey, fg="#00aa44")

        # Show confirm/cancel buttons
        btn_frame.pack(pady=5)

        return "break"

    def _confirm() -> None:
        if captured_hotkey[0]:
            on_captured(captured_hotkey[0])
        root.destroy()

    def _cancel() -> None:
        root.destroy()

    btn_frame = tk.Frame(root)
    tk.Button(btn_frame, text="  OK  ", command=_confirm, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", command=_cancel, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)

    root.bind("<Key>", _on_key)
    root.mainloop()
