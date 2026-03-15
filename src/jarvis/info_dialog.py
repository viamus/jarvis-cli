"""System info dialog for Jarvis."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jarvis.daemon import Daemon


def show_info(daemon: Daemon) -> None:
    """Show a system info dialog with model and device details."""
    t = daemon._transcriber

    gpu_name = "N/A"
    if t.device == "cuda":
        try:
            import torch
            gpu_name = torch.cuda.get_device_name(0)
        except Exception:
            gpu_name = "CUDA (unknown)"

    root = tk.Tk()
    root.title("Jarvis — System Info")
    root.geometry("340x260")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # Center on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 340) // 2
    y = (root.winfo_screenheight() - 260) // 2
    root.geometry(f"+{x}+{y}")

    title = tk.Label(root, text="Jarvis Voice", font=("Segoe UI", 14, "bold"), pady=8)
    title.pack()

    info_frame = tk.Frame(root, padx=20)
    info_frame.pack(fill=tk.BOTH, expand=True)

    rows = [
        ("Model", t.model_name),
        ("Device", t.device.upper()),
        ("GPU", gpu_name),
        ("Compute", t.compute_type),
        ("Hotkey", daemon._hotkey),
        ("Language", "pt (Portuguese)"),
    ]

    for i, (label, value) in enumerate(rows):
        tk.Label(
            info_frame,
            text=f"{label}:",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).grid(row=i, column=0, sticky="w", pady=2)
        tk.Label(
            info_frame,
            text=value,
            font=("Segoe UI", 10),
            anchor="w",
            fg="#0088aa",
        ).grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)

    tk.Button(
        root,
        text="  OK  ",
        command=root.destroy,
        font=("Segoe UI", 10),
    ).pack(pady=10)

    root.mainloop()
