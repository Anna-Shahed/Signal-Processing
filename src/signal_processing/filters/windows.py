"""Window functions for spectral analysis and FIR design."""

from __future__ import annotations

import numpy as np
from scipy.signal import get_window as scipy_get_window
from scipy.signal.windows import kaiser as scipy_kaiser

from ..utils.validation import SignalValidationError


def _validate_length(length: int) -> int:
    length = int(length)
    if length <= 0:
        raise SignalValidationError("Window length must be positive.")
    return length


def rectangular(length: int) -> np.ndarray:
    """Return a rectangular (boxcar) window."""
    return np.ones(_validate_length(length), dtype=float)


def hann(length: int) -> np.ndarray:
    """Return a periodic Hann window."""
    return np.asarray(scipy_get_window("hann", length, fftbins=True), dtype=float)


def hamming(length: int) -> np.ndarray:
    """Return a periodic Hamming window."""
    return np.asarray(scipy_get_window("hamming", length, fftbins=True), dtype=float)


def blackman(length: int) -> np.ndarray:
    """Return a periodic Blackman window."""
    return np.asarray(scipy_get_window("blackman", length, fftbins=True), dtype=float)


def kaiser(length: int, beta: float = 14.0) -> np.ndarray:
    """Return a Kaiser window with the requested shape parameter."""
    beta = float(beta)
    if beta < 0:
        raise SignalValidationError("Kaiser beta must be non-negative.")
    return np.asarray(scipy_kaiser(_validate_length(length), beta), dtype=float)


def get_window(
    window: str | tuple[str, float] | np.ndarray,
    length: int,
    *,
    periodic: bool = True,
) -> np.ndarray:
    """Resolve a named or custom window to a NumPy array.

    Supported names: rectangular, hann, hamming, blackman, kaiser.
    """
    length = _validate_length(length)

    if isinstance(window, np.ndarray):
        values = np.asarray(window, dtype=float)
        if values.ndim != 1 or values.size != length:
            raise SignalValidationError(
                "A custom window must be one-dimensional and match the requested length."
            )
        return values

    name = str(window).lower().strip()

    if name in {"rectangular", "boxcar", "rect"}:
        return rectangular(length)
    if name in {"hann", "hanning"}:
        return np.asarray(scipy_get_window("hann", length, fftbins=periodic), dtype=float)
    if name in {"hamming"}:
        return np.asarray(scipy_get_window("hamming", length, fftbins=periodic), dtype=float)
    if name in {"blackman"}:
        return np.asarray(scipy_get_window("blackman", length, fftbins=periodic), dtype=float)
    if name in {"kaiser", "kaiser-bessel"}:
        beta = 14.0
        if isinstance(window, tuple) and len(window) == 2:
            beta = float(window[1])
        return kaiser(length, beta)

    raise SignalValidationError(f"Unknown window: {window!r}.")


def apply_window(
    samples: np.ndarray,
    window: str | tuple[str, float] | np.ndarray,
    *,
    axis: int = -1,
) -> np.ndarray:
    """Multiply samples by a window along the chosen axis."""
    data = np.asarray(samples, dtype=float)
    if data.ndim == 0:
        raise SignalValidationError("samples must have at least one dimension.")

    window_values = get_window(window, data.shape[axis])
    shape = [1] * data.ndim
    shape[axis] = -1
    return data * window_values.reshape(shape)
