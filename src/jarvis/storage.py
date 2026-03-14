"""Atomic read/write of transcription JSON via filesystem."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from jarvis.config import TRANSCRIPTION_FILE, ensure_temp_dir


@dataclass
class Transcription:
    text: str
    language: str
    timestamp: str
    consumed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Transcription:
        return cls(
            text=d["text"],
            language=d["language"],
            timestamp=d["timestamp"],
            consumed=d.get("consumed", False),
        )


def save_transcription(text: str, language: str) -> Path:
    """Write transcription atomically (write tmp then rename)."""
    ensure_temp_dir()
    t = Transcription(
        text=text,
        language=language,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    tmp_path = TRANSCRIPTION_FILE.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(t.to_dict(), ensure_ascii=False), encoding="utf-8")
    # Atomic rename (on Windows, need to remove target first)
    if TRANSCRIPTION_FILE.exists():
        TRANSCRIPTION_FILE.unlink()
    os.rename(tmp_path, TRANSCRIPTION_FILE)
    return TRANSCRIPTION_FILE


def load_transcription(consume: bool = True) -> Transcription | None:
    """Load the latest transcription. If consume=True, mark it as consumed."""
    if not TRANSCRIPTION_FILE.exists():
        return None
    try:
        data = json.loads(TRANSCRIPTION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    t = Transcription.from_dict(data)
    if t.consumed:
        return None

    if consume:
        data["consumed"] = True
        tmp_path = TRANSCRIPTION_FILE.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        if TRANSCRIPTION_FILE.exists():
            TRANSCRIPTION_FILE.unlink()
        os.rename(tmp_path, TRANSCRIPTION_FILE)

    return t
