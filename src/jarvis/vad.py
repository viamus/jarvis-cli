"""Voice Activity Detection via RMS energy."""

from __future__ import annotations

import numpy as np

from jarvis.config import (
    MIN_SPEECH_DURATION,
    SAMPLE_RATE,
    SILENCE_DURATION,
    SILENCE_THRESHOLD,
)


def is_silent(chunk: np.ndarray, threshold: float = SILENCE_THRESHOLD) -> bool:
    """Return True if the RMS energy of the chunk is below threshold."""
    if chunk is None or len(chunk) == 0:
        return True
    rms = np.sqrt(np.mean(chunk**2))
    return rms < threshold


class SilenceDetector:
    """Tracks consecutive silence to decide when to stop recording."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        silence_duration: float = SILENCE_DURATION,
        min_speech_duration: float = MIN_SPEECH_DURATION,
        threshold: float = SILENCE_THRESHOLD,
    ):
        self.sample_rate = sample_rate
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        self.threshold = threshold
        self._silence_samples = 0
        self._speech_samples = 0

    def reset(self) -> None:
        self._silence_samples = 0
        self._speech_samples = 0

    def process(self, chunk: np.ndarray) -> bool:
        """Process a chunk. Returns True if recording should stop."""
        n = len(chunk)
        if is_silent(chunk, self.threshold):
            self._silence_samples += n
        else:
            self._speech_samples += n
            self._silence_samples = 0

        has_enough_speech = (
            self._speech_samples / self.sample_rate >= self.min_speech_duration
        )
        silence_exceeded = (
            self._silence_samples / self.sample_rate >= self.silence_duration
        )
        return has_enough_speech and silence_exceeded
