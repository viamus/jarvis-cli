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

from jarvis.audio_feedback import beep_ready, beep_start, beep_stop
from jarvis.config import (
    MAX_RECORDING_DURATION,
    PID_FILE,
    SAMPLE_RATE,
    ensure_temp_dir,
)
from jarvis.recorder import Recorder
from jarvis.settings import get_hotkey
from jarvis.storage import save_transcription
from jarvis.transcriber import Transcriber
from jarvis.vad import SilenceDetector


class Daemon:
    """Jarvis voice daemon."""

    def __init__(self, use_tray: bool = True) -> None:
        self._recording = False
        self._stop_requested = threading.Event()
        self._lock = threading.Lock()
        self._recorder = Recorder()
        self._vad = SilenceDetector()
        self._use_tray = use_tray
        self._tray = None
        self._hotkey = get_hotkey()
        self._shutdown_event = threading.Event()
        click.echo("Loading Whisper model...")
        self._transcriber = Transcriber()
        click.echo("Whisper model loaded.")

    def _on_hotkey(self) -> None:
        """Handle hotkey press — toggle recording on/off."""
        with self._lock:
            if self._recording:
                # Already recording — signal to stop
                self._stop_requested.set()
                return
            self._recording = True
            self._stop_requested.clear()

        threading.Thread(target=self._record_and_transcribe, daemon=True).start()

    def _record_and_transcribe(self) -> None:
        """Record audio, detect silence, transcribe, and save."""
        try:
            if self._tray:
                self._tray.set_state("recording")

            beep_start()
            self._vad.reset()
            self._recorder.start()
            click.echo("Recording...")

            start_time = time.monotonic()
            while True:
                time.sleep(0.05)  # Check every 50ms

                # Manual stop via hotkey
                if self._stop_requested.is_set():
                    click.echo("Stopped by hotkey.")
                    break

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

            if self._tray:
                self._tray.set_state("transcribing")

            click.echo("Transcribing...")
            result = self._transcriber.transcribe(audio, SAMPLE_RATE)

            if not result.text:
                click.echo("No speech detected.")
                return

            save_transcription(result.text, result.language)
            beep_ready()
            click.echo(
                f"Transcribed: \"{result.text}\" "
                f"({result.language}, {result.probability:.0%})"
            )

            # Auto-submit /jarvis to the focused terminal
            time.sleep(0.3)  # Brief pause for beep to be heard
            keyboard.write("/jarvis", delay=0.02)
            keyboard.press_and_release("enter")
        except Exception as e:
            try:
                click.echo(f"Error: {e}", err=True)
            except OSError:
                print(f"Error: {e}", file=sys.stderr, flush=True)
        finally:
            with self._lock:
                self._recording = False
            if self._tray:
                self._tray.set_state("idle")

    def write_pid(self) -> None:
        ensure_temp_dir()
        PID_FILE.write_text(str(os.getpid()))

    def remove_pid(self) -> None:
        if PID_FILE.exists():
            PID_FILE.unlink()

    def rebind_hotkey(self, new_hotkey: str) -> None:
        """Change the hotkey at runtime."""
        keyboard.remove_hotkey(self._hotkey)
        self._hotkey = new_hotkey
        keyboard.add_hotkey(self._hotkey, self._on_hotkey)
        click.echo(f"Hotkey changed to: {self._hotkey}")

    def shutdown(self) -> None:
        """Signal the daemon to shut down cleanly."""
        self.remove_pid()
        self._shutdown_event.set()
        click.echo("\nJarvis daemon stopped.")

    def run(self) -> None:
        """Start the daemon: register hotkey and block."""
        self.write_pid()
        keyboard.add_hotkey(self._hotkey, self._on_hotkey)
        click.echo(f"Jarvis daemon running. Hotkey: {self._hotkey}")

        if self._use_tray:
            self._run_with_tray()
        else:
            self._run_console()

    def _run_with_tray(self) -> None:
        """Run with system tray icon (no console needed)."""
        from jarvis.tray import TrayIcon

        self._tray = TrayIcon(self)

        # Run keyboard listener in a background thread
        def _keyboard_thread():
            self._shutdown_event.wait()

        kb_thread = threading.Thread(target=_keyboard_thread, daemon=True)
        kb_thread.start()

        click.echo("Jarvis is in the system tray. Right-click the icon to quit.")

        # Tray icon blocks the main thread — when it exits, we clean up
        self._tray.run()
        self.remove_pid()

    def _run_console(self) -> None:
        """Run in console mode (original behavior)."""
        click.echo("Press Ctrl+C to stop.")

        def _shutdown_signal(signum, frame):
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown_signal)
        signal.signal(signal.SIGTERM, _shutdown_signal)

        try:
            keyboard.wait()  # Block forever
        except KeyboardInterrupt:
            _shutdown_signal(None, None)
