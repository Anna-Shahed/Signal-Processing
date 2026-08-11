"""Frequency-swept chirp signal generators."""

from __future__ import annotations

import numpy as np
from scipy.signal import chirp as scipy_chirp

from ..core import Signal
from ..utils.validation import SignalValidationError
from .sinusoidal import _timebase


def _chirp(
    method: str,
    f0: float,
    f1: float,
    amplitude: float,
    phase: float,
    duration: float,
    sampling_rate: float,
    *,
    vertex_zero: bool = True,
    name: str,
) -> Signal:
    f0 = float(f0)
    f1 = float(f1)
    amplitude = float(amplitude)
    phase = float(phase)

    if not np.isfinite(f0) or f0 < 0:
        raise SignalValidationError("f0 must be finite and non-negative.")
    if not np.isfinite(f1) or f1 < 0:
        raise SignalValidationError("f1 must be finite and non-negative.")
    if not np.isfinite(amplitude):
        raise SignalValidationError("amplitude must be finite.")
    if not np.isfinite(phase):
        raise SignalValidationError("phase must be finite.")
    if method == "logarithmic" and (f0 <= 0 or f1 <= 0):
        raise SignalValidationError(
            "Logarithmic chirps require strictly positive f0 and f1."
        )

    time = _timebase(duration, sampling_rate)
    phase_degrees = np.degrees(phase)
    values = scipy_chirp(
        time,
        f0=f0,
        f1=f1,
        t1=float(duration),
        method=method,
        phi=phase_degrees,
        vertex_zero=vertex_zero,
    )
    samples = amplitude * values

    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name,
        metadata={
            "generator": name,
            "method": method,
            "f0": f0,
            "f1": f1,
            "amplitude": amplitude,
            "phase": phase,
            "vertex_zero": vertex_zero,
        },
    )


def linear_chirp(
    f0: float,
    f1: float,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    amplitude: float = 1.0,
    phase: float = 0.0,
) -> Signal:
    """Generate a linear-frequency chirp."""
    return _chirp(
        "linear",
        f0,
        f1,
        amplitude,
        phase,
        duration,
        sampling_rate,
        name="linear_chirp",
    )


def logarithmic_chirp(
    f0: float,
    f1: float,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    amplitude: float = 1.0,
    phase: float = 0.0,
) -> Signal:
    """Generate a logarithmic-frequency chirp."""
    return _chirp(
        "logarithmic",
        f0,
        f1,
        amplitude,
        phase,
        duration,
        sampling_rate,
        name="logarithmic_chirp",
    )


def quadratic_chirp(
    f0: float,
    f1: float,
    duration: float = 1.0,
    sampling_rate: float = 1000.0,
    *,
    amplitude: float = 1.0,
    phase: float = 0.0,
    vertex_zero: bool = True,
) -> Signal:
    """Generate a quadratic-frequency chirp."""
    return _chirp(
        "quadratic",
        f0,
        f1,
        amplitude,
        phase,
        duration,
        sampling_rate,
        vertex_zero=vertex_zero,
        name="quadratic_chirp",
    )
