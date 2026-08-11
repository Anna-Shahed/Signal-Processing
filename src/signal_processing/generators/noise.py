"""Reproducible noise generators."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import numpy as np

from ..core import Signal
from ..utils.validation import SignalValidationError, validate_sampling_rate
from .sinusoidal import _timebase


def _rng(seed: int | np.random.Generator | None) -> np.random.Generator:
    """Create or reuse a NumPy random generator."""
    if isinstance(seed, np.random.Generator):
        return seed
    return np.random.default_rng(seed)


def _noise_length(duration: float, sampling_rate: float) -> int:
    """Validate a duration/rate pair and return its sample count."""
    return _timebase(duration, sampling_rate).size


def gaussian_noise(
    duration: float,
    sampling_rate: float,
    *,
    mean: float = 0.0,
    standard_deviation: float = 1.0,
    seed: int | np.random.Generator | None = None,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate Gaussian noise."""
    mean = float(mean)
    standard_deviation = float(standard_deviation)
    validate_sampling_rate(sampling_rate)

    if not np.isfinite(mean):
        raise SignalValidationError("mean must be finite.")
    if not np.isfinite(standard_deviation) or standard_deviation < 0:
        raise SignalValidationError(
            "standard_deviation must be finite and non-negative."
        )

    samples = _rng(seed).normal(
        loc=mean,
        scale=standard_deviation,
        size=_noise_length(duration, sampling_rate),
    )
    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "gaussian_noise",
        units=units,
        metadata={
            "generator": "gaussian_noise",
            "mean": mean,
            "standard_deviation": standard_deviation,
            "seed": seed if isinstance(seed, int) else None,
        },
    )


def white_noise(
    duration: float,
    sampling_rate: float,
    *,
    amplitude: float = 1.0,
    seed: int | np.random.Generator | None = None,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate zero-mean white Gaussian noise with the requested RMS scale."""
    amplitude = float(amplitude)
    if not np.isfinite(amplitude) or amplitude < 0:
        raise SignalValidationError("amplitude must be finite and non-negative.")

    return gaussian_noise(
        duration,
        sampling_rate,
        standard_deviation=amplitude,
        seed=seed,
        name=name or "white_noise",
        units=units,
    )


def uniform_noise(
    duration: float,
    sampling_rate: float,
    *,
    low: float = -1.0,
    high: float = 1.0,
    seed: int | np.random.Generator | None = None,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate uniformly distributed noise."""
    low = float(low)
    high = float(high)
    validate_sampling_rate(sampling_rate)

    if not np.isfinite(low) or not np.isfinite(high) or low >= high:
        raise SignalValidationError("uniform noise requires finite low < high.")

    samples = _rng(seed).uniform(
        low=low,
        high=high,
        size=_noise_length(duration, sampling_rate),
    )
    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "uniform_noise",
        units=units,
        metadata={
            "generator": "uniform_noise",
            "low": low,
            "high": high,
            "seed": seed if isinstance(seed, int) else None,
        },
    )


def pink_noise(
    duration: float,
    sampling_rate: float,
    *,
    amplitude: float = 1.0,
    seed: int | np.random.Generator | None = None,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate approximate 1/f pink noise using frequency-domain shaping."""
    amplitude = float(amplitude)
    if not np.isfinite(amplitude) or amplitude < 0:
        raise SignalValidationError("amplitude must be finite and non-negative.")

    n_samples = _noise_length(duration, sampling_rate)
    generator = _rng(seed)
    white = generator.normal(size=n_samples)

    spectrum = np.fft.rfft(white)
    frequencies = np.fft.rfftfreq(n_samples, d=1.0 / sampling_rate)

    if frequencies.size > 1:
        frequencies[0] = frequencies[1]
    else:
        frequencies[0] = 1.0

    shaped = spectrum / np.sqrt(frequencies)
    samples = np.fft.irfft(shaped, n=n_samples)
    samples -= np.mean(samples)

    standard_deviation = np.std(samples)
    if standard_deviation > 0:
        samples = samples / standard_deviation * amplitude

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "pink_noise",
        units=units,
        metadata={
            "generator": "pink_noise",
            "amplitude": amplitude,
            "seed": seed if isinstance(seed, int) else None,
            "method": "frequency_domain_1_over_sqrt_f",
        },
    )
