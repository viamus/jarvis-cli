"""Whisper wrapper using faster-whisper."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions

from jarvis.config import WHISPER_COMPUTE_TYPE, WHISPER_MODEL

# Technical vocabulary hint for the decoder
_INITIAL_PROMPT = (
    "commit, push, pull, branch, merge, rebase, deploy, README, "
    "refactor, endpoint, API, CLI, Docker, Kubernetes, npm, pip"
)


@dataclass
class TranscriptionResult:
    text: str
    language: str
    probability: float
    duration: float


class Transcriber:
    """Loads a Whisper model once and transcribes audio buffers."""

    def __init__(
        self,
        model_name: str = WHISPER_MODEL,
        compute_type: str = WHISPER_COMPUTE_TYPE,
    ):
        self.model = WhisperModel(model_name, device="cpu", compute_type=compute_type)

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
