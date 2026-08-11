"""Wavelet transforms with a stable package-level abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pywt

from ..core import Signal
from ..utils.validation import SignalValidationError, TransformError


@dataclass(slots=True)
class WaveletDecomposition:
    """Package-level representation of a discrete wavelet decomposition."""

    approximation: np.ndarray
    details: tuple[np.ndarray, ...]
    wavelet: str
    sampling_rate: float
    original_length: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.approximation = np.asarray(self.approximation, dtype=float)
        self.details = tuple(np.asarray(detail, dtype=float) for detail in self.details)
        self.wavelet = str(self.wavelet)
        self.sampling_rate = float(self.sampling_rate)
        self.original_length = int(self.original_length)
        self.metadata = dict(self.metadata)

        if self.approximation.ndim != 1:
            raise TransformError("approximation must be one-dimensional.")
        if any(detail.ndim != 1 for detail in self.details):
            raise TransformError("Every detail coefficient array must be one-dimensional.")
        if self.sampling_rate <= 0 or not np.isfinite(self.sampling_rate):
            raise SignalValidationError("sampling_rate must be positive and finite.")
        if self.original_length <= 0:
            raise TransformError("original_length must be positive.")

    @property
    def level(self) -> int:
        """Number of decomposition levels."""
        return len(self.details)

    def coefficients(self) -> list[np.ndarray]:
        """Return coefficients in PyWavelets-compatible coarse-to-fine order."""
        return [self.approximation, *self.details]

    def reconstruct(self, *, length: int | None = None) -> np.ndarray:
        """Reconstruct samples using the configured wavelet."""
        try:
            values = pywt.waverec(self.coefficients(), self.wavelet)
        except (ValueError, KeyError) as exc:
            raise TransformError("Wavelet reconstruction failed.") from exc

        target = self.original_length if length is None else int(length)
        if target <= 0:
            raise SignalValidationError("length must be positive.")
        return np.asarray(values[:target], dtype=float)


def _as_real_vector(values: Signal | Any) -> tuple[np.ndarray, float]:
    """Normalize wavelet input."""
    if isinstance(values, Signal):
        samples = np.asarray(values.samples, dtype=float)
        rate = values.sampling_rate
    else:
        samples = np.asarray(values, dtype=float)
        rate = 1.0

    if samples.ndim != 1 or samples.size == 0:
        raise TransformError("Wavelet input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise TransformError("Wavelet input must contain finite values.")
    return samples, rate


def dwt(
    values: Signal | Any,
    *,
    wavelet: str = "haar",
    level: int | None = None,
) -> WaveletDecomposition:
    """Perform a discrete multi-level wavelet decomposition."""
    samples, sampling_rate = _as_real_vector(values)

    try:
        wavelet_object = pywt.Wavelet(wavelet)
        maximum_level = pywt.dwt_max_level(samples.size, wavelet_object.dec_len)
    except (ValueError, TypeError) as exc:
        raise TransformError(f"Invalid wavelet: {wavelet!r}.") from exc

    if level is None:
        level = maximum_level
    level = int(level)

    if level < 1:
        raise TransformError("level must be at least one.")
    if level > maximum_level:
        raise TransformError(
            f"level={level} exceeds the maximum supported level of {maximum_level}."
        )

    coefficients = pywt.wavedec(samples, wavelet_object, level=level)
    return WaveletDecomposition(
        approximation=coefficients[0],
        details=tuple(coefficients[1:]),
        wavelet=wavelet,
        sampling_rate=sampling_rate,
        original_length=samples.size,
        metadata={
            "implementation": "pywavelets_wrapper",
            "extension_mode": "symmetric",
        },
    )


def idwt(
    decomposition: WaveletDecomposition,
    *,
    length: int | None = None,
) -> Signal:
    """Reconstruct a :class:`Signal` from a wavelet decomposition."""
    if not isinstance(decomposition, WaveletDecomposition):
        raise TransformError("idwt requires a WaveletDecomposition instance.")

    return Signal(
        samples=decomposition.reconstruct(length=length),
        sampling_rate=decomposition.sampling_rate,
        name="wavelet_reconstruction",
        metadata={
            "source": "idwt",
            "wavelet": decomposition.wavelet,
            "level": decomposition.level,
        },
    )


def haar_transform(values: Any) -> tuple[np.ndarray, np.ndarray]:
    """Perform one level of the normalized Haar transform independently.

    For an even-length input x, the coefficients are:

    ``a[k] = (x[2k] + x[2k + 1]) / sqrt(2)``

    ``d[k] = (x[2k] - x[2k + 1]) / sqrt(2)``
    """
    samples = np.asarray(values, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise TransformError("Haar input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise TransformError("Haar input must contain finite values.")
    if samples.size % 2:
        raise TransformError("The one-level Haar transform requires an even length.")

    even = samples[::2]
    odd = samples[1::2]
    scale = np.sqrt(2.0)
    return (even + odd) / scale, (even - odd) / scale


def inverse_haar_transform(
    approximation: Any,
    detail: Any,
) -> np.ndarray:
    """Reconstruct samples from one-level normalized Haar coefficients."""
    approximation = np.asarray(approximation, dtype=float)
    detail = np.asarray(detail, dtype=float)

    if approximation.ndim != 1 or detail.ndim != 1:
        raise TransformError("Haar coefficients must be one-dimensional.")
    if approximation.shape != detail.shape:
        raise TransformError("Approximation and detail arrays must have equal lengths.")
    if not np.all(np.isfinite(approximation)) or not np.all(np.isfinite(detail)):
        raise TransformError("Haar coefficients must contain finite values.")

    scale = np.sqrt(2.0)
    output = np.empty(approximation.size * 2, dtype=float)
    output[::2] = (approximation + detail) / scale
    output[1::2] = (approximation - detail) / scale
    return output
