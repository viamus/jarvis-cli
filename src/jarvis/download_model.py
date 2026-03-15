"""Download the Whisper model ahead of time with progress feedback."""

from __future__ import annotations

import click

from jarvis.config import WHISPER_MODEL
from jarvis.transcriber import _detect_device


def download() -> None:
    """Download the appropriate Whisper model based on detected device."""
    device, compute_type = _detect_device()
    model_name = WHISPER_MODEL

    if device == "cuda" and model_name == "small":
        model_name = "large-v3"

    click.echo(f"Device: {device.upper()} ({compute_type})")
    click.echo(f"Model: {model_name}")
    click.echo("Downloading model (this may take a few minutes on first run)...")

    from faster_whisper import WhisperModel

    WhisperModel(model_name, device=device, compute_type=compute_type)
    click.echo("Model downloaded and ready!")


if __name__ == "__main__":
    download()
