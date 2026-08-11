"""Educational direct discrete Fourier transform implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..core import Signal, Spectrum
from ..utils.validation import SignalValidationError, TransformError


def _as_vector(values: Any) -> np.ndarray:
    """Convert a signal or array-like input to a one-dimensional complex vector."""
    if isinstance(values, Signal):
        values = values.samples

    array = np.asarray(values, dtype=complex)
    if array.ndim != 1 or array.size == 0:
        raise TransformError("Transform input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(array)):
        raise TransformError("Transform input must contain finite values.")
    return array


def dft_educational(values: Any, *, n: int | None = None) -> np.ndarray:
    """Compute the DFT directly in O(N²) time.

    This implementation intentionally does not call an FFT routine.
    """
    input_values = _as_vector(values)

    if n is None:
        n = input_values.size
    n = int(n)
    if n <= 0:
        raise TransformError("n must be positive.")
    if n < input_values.size:
        raise TransformError("n cannot be smaller than the input length.")

    padded = np.zeros(n, dtype=complex)
    padded[: input_values.size] = input_values

    output = np.zeros(n, dtype=complex)
    for k in range(n):
        total = 0.0j
        for index in range(n):
            angle = -2.0j * np.pi * k * index / n
            total += padded[index] * np.exp(angle)
        output[k] = total

    return output


def idft_educational(values: Any, *, n: int | None = None) -> np.ndarray:
    """Compute the inverse DFT directly in O(N²) time."""
    spectrum = _as_vector(values)

    if n is None:
        n = spectrum.size
    n = int(n)
    if n <= 0:
        raise TransformError("n must be positive.")
    if n != spectrum.size:
        raise TransformError(
            "For the direct inverse DFT, n must equal the spectrum length."
        )

    output = np.zeros(n, dtype=complex)
    for index in range(n):
        total = 0.0j
        for k in range(n):
            angle = 2.0j * np.pi * k * index / n
            total += spectrum[k] * np.exp(angle)
        output[index] = total / n

    return output


def dft(
    values: Signal | Any,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    one_sided: bool = False,
) -> Spectrum:
    """Compute a direct DFT and return a :class:`Spectrum`."""
    if isinstance(values, Signal):
        input_values = values.samples
        rate = values.sampling_rate
    else:
        input_values = values
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when values is not a Signal."
            )
        rate = float(sampling_rate)

    samples = _as_vector(input_values)
    original_length = samples.size
    spectrum = dft_educational(samples, n=n)
    transform_length = spectrum.size

    if one_sided:
        if np.iscomplexobj(samples) and np.any(np.abs(samples.imag) > 1e-12):
            raise TransformError("A one-sided spectrum requires real-valued input.")
        count = transform_length // 2 + 1
        spectrum = spectrum[:count]
        frequencies = np.fft.rfftfreq(transform_length, d=1.0 / rate)
    else:
        frequencies = np.fft.fftfreq(transform_length, d=1.0 / rate)

    return Spectrum(
        frequencies=frequencies,
        values=spectrum,
        sampling_rate=rate,
        original_length=original_length,
        one_sided=one_sided,
        metadata={
            "implementation": "educational_direct_dft",
            "transform_length": transform_length,
        },
    )


def idft(values: Any) -> np.ndarray:
    """Alias for :func:`idft_educational`."""
    return idft_educational(values)
