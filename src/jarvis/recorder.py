"""Audio capture via sounddevice at 16 kHz mono float32."""

from __future__ import annotations

import numpy as np
import sounddevice as sd

from jarvis.config import CHANNELS, SAMPLE_RATE


class Recorder:
    """Records audio from the default microphone."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self._buffer: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._latest_chunk: np.ndarray | None = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        chunk = indata[:, 0].copy()  # mono
        self._buffer.append(chunk)
        self._latest_chunk = chunk

    def start(self) -> None:
        """Start recording."""
        self._buffer = []
        self._latest_chunk = None
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return the full audio buffer as a 1D float32 array."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._buffer:
            return np.array([], dtype=np.float32)
        return np.concatenate(self._buffer)

    def get_latest_chunk(self) -> np.ndarray | None:
        """Return the most recent audio chunk (for VAD)."""
        return self._latest_chunk
