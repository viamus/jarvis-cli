"""Persistent settings for Jarvis-CLI."""

from __future__ import annotations

import json
from pathlib import Path

from jarvis.config import ensure_temp_dir

_SETTINGS_FILE = ensure_temp_dir() / "settings.json"

_DEFAULTS = {
    "hotkey": "ctrl+alt+j",
}


def load() -> dict:
    """Load settings from disk, returning defaults for missing keys."""
    data = {}
    if _SETTINGS_FILE.exists():
        try:
            data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {**_DEFAULTS, **data}


def save(settings: dict) -> None:
    """Save settings to disk."""
    ensure_temp_dir()
    _SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_hotkey() -> str:
    """Get the configured hotkey."""
    return load()["hotkey"]


def set_hotkey(hotkey: str) -> None:
    """Update the hotkey setting."""
    settings = load()
    settings["hotkey"] = hotkey
    save(settings)
