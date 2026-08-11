"""Convolution implementations and comparison helpers."""

from __future__ import annotations

from typing import Literal

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


def direct_convolve(
    signal: Signal | np.ndarray,
    kernel: Signal | np.ndarray,
) -> np.ndarray:
    """Convolve using a direct O(NM) implementation.

    This is provided for educational comparison and validation; production
    code should prefer :func:`convolve`.
    """
    signal_values = _as_1d(signal, "signal")
    kernel_values = _as_1d(kernel, "kernel")

    output_length = signal_values.size + kernel_values.size - 1
    output = np.zeros(output_length, dtype=float)

    for index, value in enumerate(kernel_values):
        if value != 0.0:
            output[index : index + signal_values.size] += value * signal_values

    return output


def circular_convolve(
    signal: Signal | np.ndarray,
    kernel: Signal | np.ndarray,
    *,
    mode: Literal["full", "same", "valid"] = "full",
) -> np.ndarray:
    """Convolve by circular (DFT-based) multiplication.

    The result is returned with the requested linear-convolution shape:
    ``full`` uses no trimming, ``same`` preserves the signal length, and
    ``valid`` excludes non-overlapping tail samples.
    """
    signal_values = _as_1d(signal, "signal")
    kernel_values = _as_1d(kernel, "kernel")

    linear_length = signal_values.size + kernel_values.size - 1
    transform_length = int(2 ** np.ceil(np.log2(linear_length)))

    spectrum = np.fft.rfft(signal_values, n=transform_length)
    kernel_spectrum = np.fft.rfft(kernel_values, n=transform_length)
    result = np.fft.irfft(spectrum * kernel_spectrum, n=transform_length)

    if mode == "full":
        return result[:linear_length]
    if mode == "same":
        start = (kernel_values.size - 1) // 2
        return result[start : start + signal_values.size]
    if mode == "valid":
        if kernel_values.size > signal_values.size:
            raise SignalValidationError(
                "For 'valid' mode the kernel must not exceed the signal length."
            )
        return result[kernel_values.size - 1 : signal_values.size]
    raise SignalValidationError("mode must be 'full', 'same', or 'valid'.")


def convolve(
    signal: Signal | np.ndarray,
    kernel: Signal | np.ndarray,
    *,
    mode: Literal["full", "same", "valid"] = "full",
    method: Literal["auto", "direct", "fft"] = "auto",
) -> np.ndarray:
    """Convolve a signal with a kernel.

    ``auto`` selects the FFT path for large kernels and the direct path for
    small ones; both match the reference linear convolution.
    """
    signal_values = _as_1d(signal, "signal")
    kernel_values = _as_1d(kernel, "kernel")

    if method == "direct":
        result = direct_convolve(signal_values, kernel_values)
    elif method == "fft":
        result = circular_convolve(signal_values, kernel_values, mode="full")
    elif method == "auto":
        if signal_values.size * kernel_values.size <= 4096:
            result = direct_convolve(signal_values, kernel_values)
        else:
            result = circular_convolve(signal_values, kernel_values, mode="full")
    else:
        raise SignalValidationError("method must be 'auto', 'direct', or 'fft'.")

    if mode == "full":
        return result
    if mode == "same":
        start = (kernel_values.size - 1) // 2
        return result[start : start + signal_values.size]
    if mode == "valid":
        if kernel_values.size > signal_values.size:
            raise SignalValidationError(
                "For 'valid' mode the kernel must not exceed the signal length."
            )
        return result[kernel_values.size - 1 : signal_values.size]
    raise SignalValidationError("mode must be 'full', 'same', or 'valid'.")


def convolve_fft(
    signal: Signal | np.ndarray,
    kernel: Signal | np.ndarray,
    *,
    mode: Literal["full", "same", "valid"] = "full",
) -> np.ndarray:
    """Alias for FFT-based convolution, which is O(N log N)."""
    return convolve(signal, kernel, mode=mode, method="fft")
