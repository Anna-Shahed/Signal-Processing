"""Educational and production FFT implementations."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..core import Signal, Spectrum
from ..utils.validation import SignalValidationError, TransformError


def _as_vector(values: Any) -> np.ndarray:
    """Convert input to a finite one-dimensional complex vector."""
    if isinstance(values, Signal):
        values = values.samples

    array = np.asarray(values, dtype=complex)
    if array.ndim != 1 or array.size == 0:
        raise TransformError("Transform input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(array)):
        raise TransformError("Transform input must contain finite values.")
    return array


def _is_power_of_two(value: int) -> bool:
    """Return whether a positive integer is a power of two."""
    return value > 0 and (value & (value - 1)) == 0


def _prepare(values: Any, n: int | None) -> np.ndarray:
    """Validate and optionally zero-pad transform input."""
    array = _as_vector(values)
    target = array.size if n is None else int(n)

    if target <= 0:
        raise TransformError("n must be positive.")
    if target < array.size:
        raise TransformError("n cannot be smaller than the input length.")

    padded = np.zeros(target, dtype=complex)
    padded[: array.size] = array
    return padded


def fft_radix2_educational(values: Any, *, n: int | None = None) -> np.ndarray:
    """Compute a radix-2 Cooley–Tukey FFT in O(N log N) time.

    The educational implementation requires a power-of-two transform length.
    """
    data = _prepare(values, n)
    size = data.size

    if not _is_power_of_two(size):
        raise TransformError(
            "fft_radix2_educational requires a power-of-two transform length."
        )

    indices = np.arange(size)
    reversed_indices = np.zeros(size, dtype=int)
    bits = int(np.log2(size))

    for index in range(size):
        value = index
        reversed_value = 0
        for _ in range(bits):
            reversed_value = (reversed_value << 1) | (value & 1)
            value >>= 1
        reversed_indices[index] = reversed_value

    output = data[reversed_indices].copy()
    block_length = 2

    while block_length <= size:
        half = block_length // 2
        twiddle = np.exp(-2.0j * np.pi * np.arange(half) / block_length)

        for block_start in range(0, size, block_length):
            first = output[block_start : block_start + half].copy()
            second = output[block_start + half : block_start + block_length].copy()
            product = twiddle * second
            output[block_start : block_start + half] = first + product
            output[block_start + half : block_start + block_length] = first - product

        block_length *= 2

    del indices
    return output


def ifft_radix2_educational(values: Any, *, n: int | None = None) -> np.ndarray:
    """Compute the inverse radix-2 FFT using conjugation."""
    spectrum = _as_vector(values)
    target = spectrum.size if n is None else int(n)

    if target != spectrum.size:
        raise TransformError("n must equal the spectrum length for inverse FFT.")
    if not _is_power_of_two(target):
        raise TransformError(
            "ifft_radix2_educational requires a power-of-two transform length."
        )

    return np.conjugate(
        fft_radix2_educational(np.conjugate(spectrum))
    ) / target


def frequency_bins(
    n: int,
    sampling_rate: float,
    *,
    one_sided: bool = False,
) -> np.ndarray:
    """Return FFT frequency bins."""
    n = int(n)
    sampling_rate = float(sampling_rate)

    if n <= 0:
        raise TransformError("n must be positive.")
    if not np.isfinite(sampling_rate) or sampling_rate <= 0:
        raise SignalValidationError("sampling_rate must be positive and finite.")

    if one_sided:
        return np.fft.rfftfreq(n, d=1.0 / sampling_rate)
    return np.fft.fftfreq(n, d=1.0 / sampling_rate)


def fft(
    values: Signal | Any,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    one_sided: bool = False,
) -> Spectrum:
    """Compute a production FFT using NumPy and return a :class:`Spectrum`."""
    if isinstance(values, Signal):
        samples = values.samples
        rate = values.sampling_rate
    else:
        samples = values
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when values is not a Signal."
            )
        rate = float(sampling_rate)

    input_values = _as_vector(samples)
    original_length = input_values.size
    target = input_values.size if n is None else int(n)

    if target < input_values.size or target <= 0:
        raise TransformError("n must be positive and at least the input length.")

    if one_sided:
        if np.any(np.abs(input_values.imag) > 1e-12):
            raise TransformError("A one-sided spectrum requires real-valued input.")
        values_out = np.fft.rfft(input_values.real, n=target)
    else:
        values_out = np.fft.fft(input_values, n=target)

    return Spectrum(
        frequencies=frequency_bins(target, rate, one_sided=one_sided),
        values=values_out,
        sampling_rate=rate,
        original_length=original_length,
        one_sided=one_sided,
        metadata={
            "implementation": "numpy_fft",
            "transform_length": target,
        },
    )


def real_fft(
    values: Signal | Any,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
) -> Spectrum:
    """Compute a one-sided production FFT for real-valued input."""
    return fft(
        values,
        sampling_rate=sampling_rate,
        n=n,
        one_sided=True,
    )


def ifft(values: Spectrum | Any, *, n: int | None = None) -> np.ndarray:
    """Compute an inverse production FFT.

    A one-sided :class:`Spectrum` is reconstructed with ``irfft`` and uses its
    original signal length unless an explicit length is supplied.
    """
    if isinstance(values, Spectrum):
        if values.one_sided:
            target = values.original_length if n is None else int(n)
            return np.fft.irfft(values.values, n=target)
        target = values.original_length if n is None else int(n)
        return np.fft.ifft(values.values, n=target)

    spectrum = _as_vector(values)
    target = spectrum.size if n is None else int(n)
    if target != spectrum.size:
        raise TransformError("n must equal the spectrum length for a full inverse FFT.")
    return np.fft.ifft(spectrum, n=target)
