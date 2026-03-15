"""Jarvis CLI — voice middleware for Claude Code."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from jarvis.config import HOTKEY, PID_FILE, SAMPLE_RATE, ensure_temp_dir


@click.group()
def cli() -> None:
    """Jarvis: voice middleware for Claude Code."""
    pass


@cli.command()
@click.option("--no-tray", is_flag=True, help="Run in console mode without system tray icon.")
def daemon(no_tray: bool) -> None:
    """Start the Jarvis voice daemon (blocks)."""
    from jarvis.daemon import Daemon

    d = Daemon(use_tray=not no_tray)
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


@cli.command("install-skill")
def install_skill() -> None:
    """Install the /jarvis skill into Claude Code."""
    import tempfile

    skill_dir = Path.home() / ".claude" / "skills" / "jarvis"
    skill_file = skill_dir / "SKILL.md"

    # Use forward slashes so bash doesn't eat the backslashes
    python_exe = Path(sys.executable).as_posix()
    json_path = (Path(tempfile.gettempdir()) / "jarvis-cli" / "last_transcription.json").as_posix()

    skill_content = f"""---
name: jarvis
description: Read voice transcription from Jarvis daemon and use it as the user's spoken request. Use when the user invokes /jarvis.
---

The user spoke the following request via voice (transcribed by Jarvis voice middleware).
Treat it as if the user typed it directly. Respond in the same language as the transcription.

!`{python_exe} -c "import json; f=r'{json_path}'; d=json.load(open(f,encoding='utf-8')); assert not d.get('consumed'), 'NO_TRANSCRIPTION'; d['consumed']=True; json.dump(d,open(f,'w',encoding='utf-8'),ensure_ascii=False); print(d['text'])"`
"""

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(skill_content.strip() + "\n", encoding="utf-8")
    click.echo(f"Jarvis skill installed at {skill_file}")
    click.echo("Use /jarvis in Claude Code to send voice transcriptions.")


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
