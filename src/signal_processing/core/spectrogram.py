"""Time-frequency data model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..utils.validation import SignalValidationError, validate_metadata, validate_sampling_rate


@dataclass(slots=True)
class Spectrogram:
    """Short-time Fourier transform representation."""

    times: np.ndarray
    frequencies: np.ndarray
    values: np.ndarray
    sampling_rate: float
    window: str
    hop_length: int
    one_sided: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.times = np.asarray(self.times, dtype=float)
        self.frequencies = np.asarray(self.frequencies, dtype=float)
        self.values = np.asarray(self.values, dtype=complex)

        if self.times.ndim != 1 or self.frequencies.ndim != 1:
            raise SignalValidationError("times and frequencies must be one-dimensional.")
        if self.values.ndim != 2:
            raise SignalValidationError("values must be a two-dimensional time-frequency array.")
        expected_shape = (self.frequencies.size, self.times.size)
        if self.values.shape != expected_shape:
            raise SignalValidationError(
                "values must have shape (n_frequencies, n_times)."
            )
        if not np.all(np.isfinite(self.times)):
            raise SignalValidationError("times must be finite.")
        if not np.all(np.isfinite(self.frequencies)):
            raise SignalValidationError("frequencies must be finite.")
        if not np.all(np.isfinite(self.values)):
            raise SignalValidationError("values must be finite.")

        self.sampling_rate = validate_sampling_rate(self.sampling_rate)
        self.window = str(self.window)
        self.hop_length = int(self.hop_length)
        if self.hop_length <= 0:
            raise SignalValidationError("hop_length must be positive.")
        self.one_sided = bool(self.one_sided)
        self.metadata = validate_metadata(self.metadata)

    @property
    def magnitude(self) -> np.ndarray:
        """Magnitude of the STFT."""
        return np.abs(self.values)

    @property
    def power(self) -> np.ndarray:
        """Squared magnitude of the STFT."""
        return np.square(self.magnitude)

    @property
    def duration(self) -> float:
        """Time span covered by the spectrogram."""
        if self.times.size == 0:
            return 0.0
        return float(self.times[-1] - self.times[0])

    def to_dict(self) -> dict[str, Any]:
        """Serialize the spectrogram without losing complex values."""
        return {
            "times": self.times.tolist(),
            "frequencies": self.frequencies.tolist(),
            "values_real": self.values.real.tolist(),
            "values_imag": self.values.imag.tolist(),
            "sampling_rate": self.sampling_rate,
            "window": self.window,
            "hop_length": self.hop_length,
            "one_sided": self.one_sided,
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the spectrogram to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Spectrogram:
        """Construct a spectrogram from serialized data."""
        try:
            values = np.asarray(data["values_real"]) + 1j * np.asarray(data["values_imag"])
            return cls(
                times=data["times"],
                frequencies=data["frequencies"],
                values=values,
                sampling_rate=data["sampling_rate"],
                window=data["window"],
                hop_length=data["hop_length"],
                one_sided=data.get("one_sided", True),
                metadata=data.get("metadata", {}),
            )
        except KeyError as exc:
            raise SignalValidationError(
                f"Missing spectrogram field: {exc.args[0]}."
            ) from exc

    @classmethod
    def from_json(cls, text: str) -> Spectrogram:
        """Construct a spectrogram from JSON text."""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SignalValidationError("Invalid spectrogram JSON.") from exc
        if not isinstance(data, dict):
            raise SignalValidationError("Spectrogram JSON must contain an object.")
        return cls.from_dict(data)
