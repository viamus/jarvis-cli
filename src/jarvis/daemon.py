"""Main daemon: hotkey listener -> record -> transcribe -> save."""

from __future__ import annotations

import os
import signal
import sys
import threading
import time

import click
import keyboard
import numpy as np

from jarvis.audio_feedback import beep_start, beep_stop
from jarvis.config import (
    HOTKEY,
    MAX_RECORDING_DURATION,
    PID_FILE,
    SAMPLE_RATE,
    ensure_temp_dir,
)
from jarvis.recorder import Recorder
from jarvis.storage import save_transcription
from jarvis.transcriber import Transcriber
from jarvis.vad import SilenceDetector


class Daemon:
    """Jarvis voice daemon."""

    def __init__(self) -> None:
        self._recording = False
        self._lock = threading.Lock()
        self._recorder = Recorder()
        self._vad = SilenceDetector()
        click.echo("Loading Whisper model...")
        self._transcriber = Transcriber()
        click.echo("Whisper model loaded.")

    def _on_hotkey(self) -> None:
        """Handle hotkey press — toggle recording."""
        with self._lock:
            if self._recording:
                return  # Already recording, ignore
            self._recording = True

        threading.Thread(target=self._record_and_transcribe, daemon=True).start()

    def _record_and_transcribe(self) -> None:
        """Record audio, detect silence, transcribe, and save."""
        try:
            beep_start()
            self._vad.reset()
            self._recorder.start()
            click.echo("Recording...")

            start_time = time.monotonic()
            while True:
                time.sleep(0.05)  # Check every 50ms

                # Hard time limit
                elapsed = time.monotonic() - start_time
                if elapsed >= MAX_RECORDING_DURATION:
                    click.echo("Max recording duration reached.")
                    break

                # VAD check
                chunk = self._recorder.get_latest_chunk()
                if chunk is not None and self._vad.process(chunk):
                    click.echo("Silence detected, stopping.")
                    break

            audio = self._recorder.stop()
            beep_stop()

            if len(audio) < SAMPLE_RATE * 0.3:
                click.echo("Audio too short, discarding.")
                return

            click.echo("Transcribing...")
            result = self._transcriber.transcribe(audio, SAMPLE_RATE)

            if not result.text:
                click.echo("No speech detected.")
                return

            save_transcription(result.text, result.language)
            click.echo(
                f"Transcribed: \"{result.text}\" "
                f"({result.language}, {result.probability:.0%})"
            )
        except Exception as e:
            try:
                click.echo(f"Error: {e}", err=True)
            except OSError:
                print(f"Error: {e}", file=sys.stderr, flush=True)
        finally:
            with self._lock:
                self._recording = False

    def write_pid(self) -> None:
        ensure_temp_dir()
        PID_FILE.write_text(str(os.getpid()))

    def remove_pid(self) -> None:
        if PID_FILE.exists():
            PID_FILE.unlink()

    def run(self) -> None:
        """Start the daemon: register hotkey and block."""
        self.write_pid()
        keyboard.add_hotkey(HOTKEY, self._on_hotkey)
        click.echo(f"Jarvis daemon running. Hotkey: {HOTKEY}")
        click.echo("Press Ctrl+C to stop.")

        def _shutdown(signum, frame):
            self.remove_pid()
            click.echo("\nJarvis daemon stopped.")
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        try:
            keyboard.wait()  # Block forever
        except KeyboardInterrupt:
            _shutdown(None, None)
