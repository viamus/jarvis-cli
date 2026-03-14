"""Jarvis CLI — voice middleware for Claude Code."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click

from jarvis.config import HOTKEY, PID_FILE, SAMPLE_RATE, ensure_temp_dir


@click.group()
def cli() -> None:
    """Jarvis: voice middleware for Claude Code."""
    pass


@cli.command()
def daemon() -> None:
    """Start the Jarvis voice daemon (blocks)."""
    from jarvis.daemon import Daemon

    d = Daemon()
    d.run()


@cli.command()
def test() -> None:
    """Record a short clip and transcribe it (for testing)."""
    from jarvis.audio_feedback import beep_start, beep_stop
    from jarvis.recorder import Recorder
    from jarvis.transcriber import Transcriber
    from jarvis.vad import SilenceDetector

    click.echo("Loading Whisper model...")
    transcriber = Transcriber()
    recorder = Recorder()
    vad = SilenceDetector()

    click.echo(f"Speak now... (silence for 1.5s stops recording)")
    beep_start()
    recorder.start()

    import time

    start = time.monotonic()
    while True:
        time.sleep(0.1)
        if time.monotonic() - start >= 30:
            break
        chunk = recorder.get_latest_chunk()
        if chunk is not None and vad.process(chunk):
            break

    audio = recorder.stop()
    beep_stop()

    if len(audio) < SAMPLE_RATE * 0.3:
        click.echo("Audio too short.")
        return

    click.echo("Transcribing...")
    result = transcriber.transcribe(audio, SAMPLE_RATE)
    click.echo(f'"{result.text}" ({result.language}, {result.probability:.0%})')


@cli.command()
def status() -> None:
    """Check if the Jarvis daemon is running."""
    if not PID_FILE.exists():
        click.echo("Jarvis daemon is not running.")
        return

    pid = int(PID_FILE.read_text().strip())
    # Check if process exists
    try:
        os.kill(pid, 0)
        click.echo(f"Jarvis daemon is running (PID {pid}).")
    except OSError:
        click.echo("Jarvis daemon is not running (stale PID file).")
        PID_FILE.unlink()


@cli.command("install-hook")
def install_hook() -> None:
    """Install the Jarvis hook into Claude Code settings."""
    settings_path = Path.home() / ".claude" / "settings.json"

    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {}

    hooks = settings.setdefault("hooks", {})
    user_prompt_hooks = hooks.setdefault("UserPromptSubmit", [])

    jarvis_command = "python -m jarvis.hook"

    # Check if already installed
    for entry in user_prompt_hooks:
        for h in entry.get("hooks", []):
            if h.get("command") == jarvis_command:
                click.echo("Jarvis hook is already installed.")
                return

    user_prompt_hooks.append(
        {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": jarvis_command,
                }
            ],
        }
    )

    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    click.echo(f"Jarvis hook installed in {settings_path}")


@cli.command("stop")
def stop_daemon() -> None:
    """Stop the running Jarvis daemon."""
    if not PID_FILE.exists():
        click.echo("Jarvis daemon is not running.")
        return

    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, 15)  # SIGTERM
        click.echo(f"Sent stop signal to daemon (PID {pid}).")
    except OSError:
        click.echo("Daemon process not found (stale PID file).")
        PID_FILE.unlink()
