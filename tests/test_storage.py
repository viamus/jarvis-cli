"""Tests for jarvis.storage."""

import json

from jarvis.config import TRANSCRIPTION_FILE, ensure_temp_dir
from jarvis.storage import Transcription, load_transcription, save_transcription


def setup_function():
    ensure_temp_dir()
    if TRANSCRIPTION_FILE.exists():
        TRANSCRIPTION_FILE.unlink()


def test_save_and_load():
    save_transcription("olá mundo", "pt")
    t = load_transcription(consume=False)
    assert t is not None
    assert t.text == "olá mundo"
    assert t.language == "pt"
    assert t.consumed is False


def test_consume_marks_as_consumed():
    save_transcription("hello world", "en")
    t = load_transcription(consume=True)
    assert t is not None
    assert t.text == "hello world"

    # Second load should return None (consumed)
    t2 = load_transcription(consume=True)
    assert t2 is None


def test_load_no_file():
    assert load_transcription() is None


def test_transcription_roundtrip():
    t = Transcription(text="test", language="en", timestamp="2024-01-01T00:00:00Z")
    d = t.to_dict()
    t2 = Transcription.from_dict(d)
    assert t2.text == t.text
    assert t2.language == t.language
    assert t2.timestamp == t.timestamp


def test_save_creates_valid_json():
    save_transcription("teste", "pt")
    data = json.loads(TRANSCRIPTION_FILE.read_text(encoding="utf-8"))
    assert "text" in data
    assert "language" in data
    assert "timestamp" in data
    assert "consumed" in data
    assert data["consumed"] is False
