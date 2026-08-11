"""Frequency-domain data model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..utils.validation import SignalValidationError, validate_metadata, validate_sampling_rate


@dataclass(slots=True)
class Spectrum:
    """A sampled complex spectrum and its frequency-bin metadata."""

    frequencies: np.ndarray
    values: np.ndarray
    sampling_rate: float
    original_length: int
    one_sided: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.frequencies = np.asarray(self.frequencies, dtype=float)
        self.values = np.asarray(self.values, dtype=complex)

        if self.frequencies.ndim != 1 or self.values.ndim != 1:
            raise SignalValidationError("frequencies and values must be one-dimensional.")
        if self.frequencies.size == 0:
            raise SignalValidationError("A spectrum must contain at least one bin.")
        if self.frequencies.shape != self.values.shape:
            raise SignalValidationError("frequencies and values must have equal lengths.")
        if not np.all(np.isfinite(self.frequencies)):
            raise SignalValidationError("frequencies must be finite.")
        if not np.all(np.isfinite(self.values)):
            raise SignalValidationError("values must be finite.")
        self.sampling_rate = validate_sampling_rate(self.sampling_rate)

        self.original_length = int(self.original_length)
        if self.original_length <= 0:
            raise SignalValidationError("original_length must be positive.")

        self.one_sided = bool(self.one_sided)
        self.metadata = validate_metadata(self.metadata)

    @property
    def magnitude(self) -> np.ndarray:
        """Absolute spectrum magnitude."""
        return np.abs(self.values)

    @property
    def phase(self) -> np.ndarray:
        """Wrapped phase in radians."""
        return np.angle(self.values)

    @property
    def power(self) -> np.ndarray:
        """Squared magnitude of each spectral bin."""
        return np.square(self.magnitude)

    @property
    def psd(self) -> np.ndarray:
        """Simple periodogram-style power spectral density estimate."""
        density = self.power / (self.sampling_rate * self.original_length)
        if self.one_sided and density.size > 2:
            density = density.copy()
            density[1:-1] *= 2.0
        return density

    @property
    def dominant_frequency(self) -> float:
        """Frequency associated with the largest magnitude bin."""
        return float(self.frequencies[int(np.argmax(self.magnitude))])

    @property
    def spectral_centroid(self) -> float:
        """Magnitude-weighted mean frequency using nonnegative frequencies."""
        weights = self.magnitude
        if self.one_sided:
            frequencies = self.frequencies
        else:
            mask = self.frequencies >= 0
            frequencies = self.frequencies[mask]
            weights = weights[mask]
        total = float(np.sum(weights))
        return 0.0 if total == 0 else float(np.sum(frequencies * weights) / total)

    @property
    def bandwidth(self) -> float:
        """Magnitude-weighted standard deviation around the centroid."""
        weights = self.magnitude
        frequencies = self.frequencies
        if not self.one_sided:
            mask = frequencies >= 0
            frequencies = frequencies[mask]
            weights = weights[mask]
        total = float(np.sum(weights))
        if total == 0:
            return 0.0
        centroid = float(np.sum(frequencies * weights) / total)
        return float(np.sqrt(np.sum(weights * (frequencies - centroid) ** 2) / total))

    def to_dict(self) -> dict[str, Any]:
        """Serialize the spectrum without losing complex values."""
        return {
            "frequencies": self.frequencies.tolist(),
            "values_real": self.values.real.tolist(),
            "values_imag": self.values.imag.tolist(),
            "sampling_rate": self.sampling_rate,
            "original_length": self.original_length,
            "one_sided": self.one_sided,
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the spectrum to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Spectrum:
        """Construct a spectrum from serialized data."""
        try:
            values = np.asarray(data["values_real"]) + 1j * np.asarray(data["values_imag"])
            return cls(
                frequencies=data["frequencies"],
                values=values,
                sampling_rate=data["sampling_rate"],
                original_length=data["original_length"],
                one_sided=data.get("one_sided", False),
                metadata=data.get("metadata", {}),
            )
        except KeyError as exc:
            raise SignalValidationError(f"Missing spectrum field: {exc.args[0]}.") from exc

    @classmethod
    def from_json(cls, text: str) -> Spectrum:
        """Construct a spectrum from JSON text."""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SignalValidationError("Invalid spectrum JSON.") from exc
        if not isinstance(data, dict):
            raise SignalValidationError("Spectrum JSON must contain an object.")
        return cls.from_dict(data)
