"""Feature extraction helpers (non-spectral, non-statistical)."""

from __future__ import annotations

import numpy as np

from ..core import AnalysisResult, Signal
from ..utils.validation import SignalValidationError


def _as_1d(signal: Signal | np.ndarray) -> np.ndarray:
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
    else:
        samples = np.asarray(signal, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")
    return samples


def zero_crossing_rate(signal: Signal | np.ndarray) -> float:
    """Return the fraction of transitions across zero."""
    samples = _as_1d(signal)
    if samples.size < 2:
        return 0.0
    return float(np.count_nonzero(np.diff(np.signbit(samples))) / (samples.size - 1))


def envelope(
    signal: Signal | np.ndarray,
    *,
    window_length: int | None = None,
) -> np.ndarray:
    """Return a sliding RMS envelope of the signal."""
    samples = _as_1d(signal)
    length = len(samples) // 20 if window_length is None else int(window_length)
    length = max(2, min(length, samples.size))

    kernel = np.ones(length) / length
    power = np.convolve(samples**2, kernel, mode="same")
    return np.sqrt(np.maximum(power, 0.0))


def extract_features(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> AnalysisResult:
    """Combine statistical and spectral features into one result."""
    from .spectral import analyze_spectral
    from .statistical import analyze_statistical

    if isinstance(signal, Signal):
        rate = signal.sampling_rate
    else:
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when analyzing a plain array."
            )
        rate = float(sampling_rate)

    statistical = analyze_statistical(signal, sampling_rate=rate)
    spectral = analyze_spectral(signal, sampling_rate=rate)

    return AnalysisResult(
        metrics={**statistical.metrics, **spectral.metrics},
        arrays=dict(spectral.arrays),
        metadata={
            "feature": "combined",
            "sampling_rate": rate,
        },
        warnings=statistical.warnings + spectral.warnings,
    )
