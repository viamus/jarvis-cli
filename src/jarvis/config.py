"""Central configuration for Jarvis-CLI."""

import os
import tempfile
from pathlib import Path

# --- Paths ---
_TEMP_DIR = Path(tempfile.gettempdir()) / "jarvis-cli"
TRANSCRIPTION_FILE = _TEMP_DIR / "last_transcription.json"
PID_FILE = _TEMP_DIR / "daemon.pid"

# --- Hotkey ---
HOTKEY = os.environ.get("JARVIS_HOTKEY", "ctrl+alt+j")

# --- Whisper ---
WHISPER_MODEL = os.environ.get("JARVIS_WHISPER_MODEL", "base")
WHISPER_COMPUTE_TYPE = "int8"

# --- Audio ---
SAMPLE_RATE = 16000
CHANNELS = 1

# --- VAD ---
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5  # seconds of silence before stopping
MIN_SPEECH_DURATION = 0.5  # minimum speech before allowing stop
MAX_RECORDING_DURATION = 30.0  # hard cap on recording length

# --- Hook ---
TRIGGER_WORDS = ["voz", "voice", "jarvis", "v"]


def ensure_temp_dir() -> Path:
    """Create the temp directory if it doesn't exist."""
    _TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return _TEMP_DIR
