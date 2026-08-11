"""Filter response computation and design helpers."""

from __future__ import annotations

import numpy as np
from scipy.signal import freqz, sosfreqz

from ..utils.validation import FilterDesignError, validate_sampling_rate


def frequency_response(
    coefficients: tuple[np.ndarray, np.ndarray] | np.ndarray,
    *,
    sampling_rate: float = 2.0 * np.pi,
    worN: int = 512,
    whole: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (frequencies, complex response) for filter coefficients.

    FIR coefficients may be passed directly as a one-dimensional array.
    """
    rate = validate_sampling_rate(sampling_rate)

    if isinstance(coefficients, np.ndarray):
        numerator = np.asarray(coefficients, dtype=float)
        denominator = np.array([1.0])
    else:
        numerator, denominator = coefficients
        numerator = np.asarray(numerator, dtype=float)
        denominator = np.asarray(denominator, dtype=float)

    if numerator.ndim != 1 or denominator.ndim != 1:
        raise FilterDesignError("Filter coefficients must be one-dimensional arrays.")

    frequencies, response = freqz(
        numerator,
        denominator,
        worN=int(worN),
        whole=whole,
        fs=rate,
    )
    return frequencies, response


def magnitude_response(
    coefficients: tuple[np.ndarray, np.ndarray] | np.ndarray,
    *,
    sampling_rate: float = 2.0 * np.pi,
    worN: int = 512,
    whole: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (frequencies, magnitude response) in linear amplitude units."""
    frequencies, response = frequency_response(
        coefficients,
        sampling_rate=sampling_rate,
        worN=worN,
        whole=whole,
    )
    return frequencies, np.abs(response)


def phase_response(
    coefficients: tuple[np.ndarray, np.ndarray] | np.ndarray,
    *,
    sampling_rate: float = 2.0 * np.pi,
    worN: int = 512,
    whole: bool = False,
    unwrap: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (frequencies, phase response) in radians."""
    frequencies, response = frequency_response(
        coefficients,
        sampling_rate=sampling_rate,
        worN=worN,
        whole=whole,
    )
    phase = np.unwrap(np.angle(response)) if unwrap else np.angle(response)
    return frequencies, phase
