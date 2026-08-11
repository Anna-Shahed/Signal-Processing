"""Sinusoidal signal generators."""

from __future__ import annotations

import numpy as np

from ..core import Signal
from ..utils.validation import SignalValidationError, validate_sampling_rate


def _timebase(duration: float, sampling_rate: float) -> np.ndarray:
    """Create a uniformly sampled time base."""
    duration = float(duration)
    sampling_rate = validate_sampling_rate(sampling_rate)

    if not np.isfinite(duration) or duration <= 0:
        raise SignalValidationError("duration must be finite and greater than zero.")

    n_samples = int(round(duration * sampling_rate))
    if n_samples < 1:
        raise SignalValidationError(
            "duration and sampling_rate must produce at least one sample."
        )

    return np.arange(n_samples, dtype=float) / sampling_rate


def sine(
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate a sinusoidal signal.

    The phase is expressed in radians and frequency in hertz.
    """
    frequency = float(frequency)
    amplitude = float(amplitude)
    phase = float(phase)

    if not np.isfinite(frequency) or frequency < 0:
        raise SignalValidationError("frequency must be finite and non-negative.")
    if not np.isfinite(amplitude):
        raise SignalValidationError("amplitude must be finite.")
    if not np.isfinite(phase):
        raise SignalValidationError("phase must be finite.")

    time = _timebase(duration, sampling_rate)
    samples = amplitude * np.sin(2.0 * np.pi * frequency * time + phase)

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "sine",
        units=units,
        metadata={
            "generator": "sine",
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
        },
    )


def cosine(
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate a cosine signal."""
    frequency = float(frequency)
    amplitude = float(amplitude)
    phase = float(phase)

    if not np.isfinite(frequency) or frequency < 0:
        raise SignalValidationError("frequency must be finite and non-negative.")
    if not np.isfinite(amplitude):
        raise SignalValidationError("amplitude must be finite.")
    if not np.isfinite(phase):
        raise SignalValidationError("phase must be finite.")

    time = _timebase(duration, sampling_rate)
    samples = amplitude * np.cos(2.0 * np.pi * frequency * time + phase)

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "cosine",
        units=units,
        metadata={
            "generator": "cosine",
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
        },
    )
