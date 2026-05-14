"""Persistent settings for Jarvis-CLI."""

from __future__ import annotations

import json
from pathlib import Path

from jarvis.config import ensure_temp_dir

_SETTINGS_FILE = ensure_temp_dir() / "settings.json"

_DEFAULTS = {
    "hotkey": "ctrl+alt+j",
    "target": "claude",
}

_TARGET_COMMANDS = {
    "claude": "/jarvis",
    "codex": "$jarvis",
}

_TARGET_LABELS = {
    "claude": "Claude Code",
    "codex": "Codex",
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


def normalize_target(target: str) -> str:
    """Normalize a target name to the stored setting value."""
    value = target.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "claude": "claude",
        "claude_code": "claude",
        "cloud": "claude",
        "codex": "codex",
    }
    if value not in aliases:
        expected = ", ".join(sorted(_TARGET_COMMANDS))
        raise ValueError(f"Unknown target {target!r}. Expected one of: {expected}")
    return aliases[value]


def get_target() -> str:
    """Get the configured assistant target."""
    try:
        return normalize_target(load()["target"])
    except ValueError:
        return _DEFAULTS["target"]


def set_target(target: str) -> str:
    """Update the assistant target setting and return its normalized value."""
    normalized = normalize_target(target)
    settings = load()
    settings["target"] = normalized
    save(settings)
    return normalized


def get_target_label(target: str | None = None) -> str:
    """Get a human-readable label for the assistant target."""
    return _TARGET_LABELS[get_target() if target is None else normalize_target(target)]


def get_target_command(target: str | None = None) -> str:
    """Get the command Jarvis should auto-type for the assistant target."""
    return _TARGET_COMMANDS[get_target() if target is None else normalize_target(target)]
