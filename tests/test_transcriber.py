"""Tests for jarvis.transcriber — only runs if faster-whisper model is available."""

import pytest
import numpy as np


@pytest.fixture
def transcriber():
    """Try to load the transcriber; skip if model not available."""
    try:
        from jarvis.transcriber import Transcriber
        return Transcriber()
    except Exception as e:
        pytest.skip(f"Whisper model not available: {e}")


def test_silence_produces_empty_text(transcriber):
    """Transcribing silence should return empty or near-empty text."""
    silence = np.zeros(16000 * 2, dtype=np.float32)  # 2 seconds of silence
    result = transcriber.transcribe(silence)
    # Whisper may return empty or very short text for silence
    assert len(result.text) < 20


def test_transcription_result_fields(transcriber):
    """Check that TranscriptionResult has the expected fields."""
    silence = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(silence)
    assert hasattr(result, "text")
    assert hasattr(result, "language")
    assert hasattr(result, "probability")
    assert hasattr(result, "duration")
    assert result.duration == pytest.approx(1.0, abs=0.1)
