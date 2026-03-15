"""Whisper wrapper using faster-whisper."""

from __future__ import annotations

from dataclasses import dataclass

import click
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions

from jarvis.config import WHISPER_MODEL

# Technical vocabulary hint for the decoder — mix of PT-BR and tech terms
_INITIAL_PROMPT = (
    "Olá, eu gostaria de fazer o seguinte: "
    "commit, push, pull, branch, merge, rebase, deploy, README, "
    "refactor, endpoint, API, CLI, Docker, Kubernetes, npm, pip, "
    "transcrição, configuração, implementação, repositório"
)


def _detect_device() -> tuple[str, str]:
    """Detect best available device. Returns (device, compute_type)."""
    try:
        import ctranslate2
        cuda_types = ctranslate2.get_supported_compute_types("cuda")
        if "float16" in cuda_types:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "float32"


@dataclass
class TranscriptionResult:
    text: str
    language: str
    probability: float
    duration: float


class Transcriber:
    """Loads a Whisper model once and transcribes audio buffers."""

    def __init__(self, model_name: str = WHISPER_MODEL):
        device, compute_type = _detect_device()
        # GPU allows larger model for much better accuracy
        if device == "cuda" and model_name == "small":
            model_name = "large-v3"
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        click.echo(f"Whisper: model={model_name}, device={device}, compute={compute_type}")
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        """Transcribe a float32 audio array. Returns TranscriptionResult."""
        duration = len(audio) / sample_rate
        segments, info = self.model.transcribe(
            audio,
            language="pt",
            initial_prompt=_INITIAL_PROMPT,
            beam_size=5,
            temperature=0,
            vad_filter=True,
            vad_parameters=VadOptions(
                min_silence_duration_ms=500,
                speech_pad_ms=300,
            ),
        )
        text = " ".join(seg.text.strip() for seg in segments)
        return TranscriptionResult(
            text=text.strip(),
            language=info.language,
            probability=info.language_probability,
            duration=duration,
        )
