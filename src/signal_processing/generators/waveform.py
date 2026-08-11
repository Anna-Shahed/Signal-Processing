"""Periodic non-sinusoidal waveform generators."""

from __future__ import annotations

import numpy as np
from scipy.signal import sawtooth as scipy_sawtooth
from scipy.signal import square as scipy_square

from ..core import Signal
from ..utils.validation import SignalValidationError, validate_sampling_rate
from .sinusoidal import _timebase


def _validate_parameters(
    frequency: float,
    amplitude: float,
    offset: float,
    phase: float,
) -> tuple[float, float, float, float]:
    frequency = float(frequency)
    amplitude = float(amplitude)
    offset = float(offset)
    phase = float(phase)

    if not np.isfinite(frequency) or frequency < 0:
        raise SignalValidationError("frequency must be finite and non-negative.")
    if not np.isfinite(amplitude):
        raise SignalValidationError("amplitude must be finite.")
    if not np.isfinite(offset):
        raise SignalValidationError("offset must be finite.")
    if not np.isfinite(phase):
        raise SignalValidationError("phase must be finite.")

    return frequency, amplitude, offset, phase


def square(
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    duty_cycle: float = 0.5,
    offset: float = 0.0,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate a square wave with configurable duty cycle."""
    frequency, amplitude, offset, phase = _validate_parameters(
        frequency, amplitude, offset, phase
    )
    validate_sampling_rate(sampling_rate)

    duty_cycle = float(duty_cycle)
    if not 0.0 < duty_cycle < 1.0:
        raise SignalValidationError("duty_cycle must be strictly between zero and one.")

    time = _timebase(duration, sampling_rate)
    base = scipy_square(
        2.0 * np.pi * frequency * time + phase,
        duty=duty_cycle,
    )
    samples = offset + amplitude * base

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "square",
        units=units,
        metadata={
            "generator": "square",
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
            "duty_cycle": duty_cycle,
            "offset": offset,
        },
    )


def triangle(
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    offset: float = 0.0,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate a symmetric triangle wave."""
    frequency, amplitude, offset, phase = _validate_parameters(
        frequency, amplitude, offset, phase
    )
    validate_sampling_rate(sampling_rate)

    time = _timebase(duration, sampling_rate)
    base = scipy_sawtooth(
        2.0 * np.pi * frequency * time + phase,
        width=0.5,
    )
    samples = offset + amplitude * base

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "triangle",
        units=units,
        metadata={
            "generator": "triangle",
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
            "offset": offset,
        },
    )


def sawtooth(
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    width: float = 1.0,
    offset: float = 0.0,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Generate a sawtooth waveform.

    ``width`` controls the location of the peak within each period. A value
    of one produces a rising sawtooth; zero produces a falling sawtooth.
    """
    frequency, amplitude, offset, phase = _validate_parameters(
        frequency, amplitude, offset, phase
    )
    validate_sampling_rate(sampling_rate)

    width = float(width)
    if not 0.0 <= width <= 1.0:
        raise SignalValidationError("width must be between zero and one.")

    time = _timebase(duration, sampling_rate)
    base = scipy_sawtooth(
        2.0 * np.pi * frequency * time + phase,
        width=width,
    )
    samples = offset + amplitude * base

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or "sawtooth",
        units=units,
        metadata={
            "generator": "sawtooth",
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
            "width": width,
            "offset": offset,
        },
    )
