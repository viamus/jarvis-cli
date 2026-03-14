"""Tests for jarvis.hook."""

import json
import subprocess
import sys

from jarvis.config import TRANSCRIPTION_FILE, ensure_temp_dir
from jarvis.storage import save_transcription


def setup_function():
    ensure_temp_dir()
    if TRANSCRIPTION_FILE.exists():
        TRANSCRIPTION_FILE.unlink()


def _run_hook(prompt: str) -> tuple[int, dict | None]:
    """Run the hook as a subprocess and return (exit_code, parsed_stdout)."""
    input_data = json.dumps({
        "prompt": prompt,
        "session_id": "test",
        "cwd": ".",
        "hook_event_name": "UserPromptSubmit",
    })
    result = subprocess.run(
        [sys.executable, "-m", "jarvis.hook"],
        input=input_data,
        capture_output=True,
        text=True,
    )
    output = None
    if result.stdout.strip():
        output = json.loads(result.stdout)
    return result.returncode, output


def test_non_trigger_passes_through():
    code, output = _run_hook("tell me about Python")
    assert code == 0
    assert output is None


def test_trigger_no_transcription():
    code, output = _run_hook("/voz")
    assert code == 2
    assert output is not None
    assert output["decision"] == "block"
    assert "No transcription" in output["reason"]


def test_trigger_with_transcription():
    save_transcription("olá mundo", "pt")
    code, output = _run_hook("/voz")
    assert code == 2
    assert output is not None
    assert output["decision"] == "block"
    assert "olá mundo" in output["reason"]
    assert "[pt]" in output["reason"]


def test_trigger_voice_alias():
    save_transcription("hello world", "en")
    code, output = _run_hook("/voice")
    assert code == 2
    assert "hello world" in output["reason"]


def test_trigger_v_alias():
    save_transcription("test", "en")
    code, output = _run_hook("/v")
    assert code == 2
    assert "test" in output["reason"]


def test_transcription_consumed_after_trigger():
    save_transcription("once only", "en")
    code1, _ = _run_hook("/voz")
    assert code1 == 2

    # Second call should have no transcription
    code2, output2 = _run_hook("/voz")
    assert code2 == 2
    assert "No transcription" in output2["reason"]
