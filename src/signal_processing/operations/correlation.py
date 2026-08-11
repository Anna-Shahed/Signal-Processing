"""Correlation implementations with lag support."""

from __future__ import annotations

import numpy as np

from ..core import Signal
from ..utils.validation import SignalValidationError


def _as_1d(values: Signal | np.ndarray, name: str) -> np.ndarray:
    if isinstance(values, Signal):
        samples = np.asarray(values.samples, dtype=float)
    else:
        samples = np.asarray(values, dtype=float)

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError(
            f"{name} must be a non-empty one-dimensional array."
        )
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError(f"{name} must contain finite values.")
    return samples


def _normalize_reference(
    reference: Signal | np.ndarray | None,
    samples: np.ndarray,
) -> np.ndarray:
    if reference is None:
        return samples
    return _as_1d(reference, "reference")


def autocorrelation(
    signal: Signal | np.ndarray,
    *,
    max_lag: int | None = None,
    mode: str = "full",
    normalize: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the autocorrelation and its lag axis.

    ``normalize=True`` divides by the zero-lag value so that the peak equals
    one.
    """
    samples = _as_1d(signal, "signal")
    full = np.correlate(samples, samples, mode="full")
    lags = np.arange(-samples.size + 1, samples.size)

    if mode == "full":
        values = full
    elif mode == "same":
        center = samples.size - 1
        values = full[center : center + samples.size]
        lags = np.arange(samples.size) - (samples.size - 1) // 2
    else:
        raise SignalValidationError("mode must be 'full' or 'same'.")

    if max_lag is not None:
        max_lag = int(max_lag)
        if max_lag < 0 or max_lag >= samples.size:
            raise SignalValidationError("max_lag must be a non-negative int below n_samples.")
        keep = np.abs(lags) <= max_lag
        values = values[keep]
        lags = lags[keep]

    if normalize:
        peak = values[np.argmax(np.abs(lags) == 0)] if samples.size else 0.0
        zero_lag = float(full[samples.size - 1])
        if zero_lag != 0:
            values = values / zero_lag
        else:
            values = np.zeros_like(values)

    return values, lags


def cross_correlation(
    signal_a: Signal | np.ndarray,
    signal_b: Signal | np.ndarray,
    *,
    mode: str = "full",
    normalize: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the cross-correlation and its lag axis.

    The result is ``sum(a[n + lag] * b[n])``, matching SciPy's definition.
    """
    a = _as_1d(signal_a, "signal_a")
    b = _as_1d(signal_b, "signal_b")
    full = np.correlate(a, b, mode="full")
    lags = np.arange(-b.size + 1, a.size)

    if mode == "full":
        values = full
    elif mode == "same":
        if b.size > a.size:
            raise SignalValidationError("For 'same' mode, signal_a must be at least as long as signal_b.")
        center = a.size - 1
        values = full[center - b.size // 2 : center + (b.size + 1) // 2]
        lags = np.arange(-(b.size // 2), (b.size + 1) // 2)
    else:
        raise SignalValidationError("mode must be 'full' or 'same'.")

    if normalize:
        denominator = np.sqrt(np.sum(a**2) * np.sum(b**2))
        if denominator > 0:
            values = values / denominator
        else:
            values = np.zeros_like(values)

    return values, lags


def normalized_cross_correlation(
    signal_a: Signal | np.ndarray,
    signal_b: Signal | np.ndarray,
    *,
    mode: str = "full",
) -> tuple[np.ndarray, np.ndarray]:
    """Alias for normalized cross-correlation in the range [-1, 1]."""
    return cross_correlation(signal_a, signal_b, mode=mode, normalize=True)
