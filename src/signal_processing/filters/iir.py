"""Infinite impulse response filter design and application."""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.signal import butter, cheby1, lfilter, sosfilt, filtfilt

from ..core import Signal
from ..utils.validation import (
    FilterDesignError,
    SignalValidationError,
    validate_sampling_rate,
)

_FilterType = Literal["lowpass", "highpass", "bandpass", "bandstop"]


def _normalized_edges(
    filter_type: _FilterType,
    cutoffs: float | tuple[float, float],
    sampling_rate: float,
) -> float | tuple[float, float]:
    rate = validate_sampling_rate(sampling_rate)
    nyquist = rate / 2.0

    if filter_type in {"lowpass", "highpass"}:
        cutoff = float(cutoffs)
        if not np.isfinite(cutoff) or cutoff <= 0 or cutoff >= nyquist:
            raise FilterDesignError(
                f"Cutoff must be finite, positive, and below Nyquist ({nyquist} Hz)."
            )
        return cutoff / nyquist

    low, high = (float(cutoffs[0]), float(cutoffs[1]))  # type: ignore[index]
    if low <= 0 or high <= low or high >= nyquist:
        raise FilterDesignError(
            "Band edges must satisfy 0 < low < high < Nyquist."
        )
    return low / nyquist, high / nyquist  # type: ignore[return-value]


def _signal_input(
    signal: Signal | np.ndarray,
    sampling_rate: float | None,
) -> tuple[np.ndarray, float, float]:
    if isinstance(signal, Signal):
        if signal.samples.ndim != 1:
            raise SignalValidationError("IIR filtering requires a one-dimensional signal.")
        return signal.samples.astype(float), signal.sampling_rate, signal.start_time

    samples = np.asarray(signal, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if sampling_rate is None:
        raise SignalValidationError(
            "sampling_rate is required when filtering a plain array."
        )
    return samples, validate_sampling_rate(sampling_rate), 0.0


def _butterworth(
    order: int,
    filter_type: _FilterType,
    cutoffs: float | tuple[float, float],
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    order = int(order)
    if order < 1:
        raise FilterDesignError("Filter order must be at least one.")
    normalized = _normalized_edges(filter_type, cutoffs, sampling_rate)
    try:
        return butter(order, normalized, btype=filter_type, output="ba")
    except ValueError as exc:
        raise FilterDesignError("Invalid Butterworth filter specification.") from exc


def _chebyshev(
    order: int,
    ripple: float,
    filter_type: _FilterType,
    cutoffs: float | tuple[float, float],
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    order = int(order)
    if order < 1:
        raise FilterDesignError("Filter order must be at least one.")
    ripple = float(ripple)
    if ripple <= 0 or not np.isfinite(ripple):
        raise FilterDesignError("Passband ripple must be finite and positive.")
    normalized = _normalized_edges(filter_type, cutoffs, sampling_rate)
    try:
        return cheby1(order, ripple, normalized, btype=filter_type, output="ba")
    except ValueError as exc:
        raise FilterDesignError("Invalid Chebyshev filter specification.") from exc


def butterworth_lowpass(
    order: int,
    cutoff: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a Butterworth low-pass filter."""
    return _butterworth(order, "lowpass", cutoff, sampling_rate)


def butterworth_highpass(
    order: int,
    cutoff: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a Butterworth high-pass filter."""
    return _butterworth(order, "highpass", cutoff, sampling_rate)


def butterworth_bandpass(
    order: int,
    cutoff_low: float,
    cutoff_high: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a Butterworth band-pass filter."""
    return _butterworth(
        order, "bandpass", (cutoff_low, cutoff_high), sampling_rate
    )


def butterworth_bandstop(
    order: int,
    cutoff_low: float,
    cutoff_high: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a Butterworth band-stop filter."""
    return _butterworth(
        order, "bandstop", (cutoff_low, cutoff_high), sampling_rate
    )


def chebyshev_lowpass(
    order: int,
    ripple: float,
    cutoff: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a type-I Chebyshev low-pass filter."""
    return _chebyshev(order, ripple, "lowpass", cutoff, sampling_rate)


def chebyshev_highpass(
    order: int,
    ripple: float,
    cutoff: float,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Design a type-I Chebyshev high-pass filter."""
    return _chebyshev(order, ripple, "highpass", cutoff, sampling_rate)


def iir_filter(
    signal: Signal | np.ndarray,
    coefficients: tuple[np.ndarray, np.ndarray],
    *,
    sampling_rate: float | None = None,
    zero_phase: bool = False,
    name: str = "iir_filtered",
) -> Signal:
    """Apply an IIR filter described by (b, a) coefficients."""
    numerator, denominator = coefficients
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)

    if numerator.ndim != 1 or denominator.ndim != 1:
        raise FilterDesignError("IIR coefficients must be one-dimensional arrays.")
    if denominator.size == 0 or denominator[0] == 0:
        raise FilterDesignError("The first denominator coefficient must be non-zero.")

    samples, rate, start_time = _signal_input(signal, sampling_rate)

    if zero_phase:
        try:
            filtered = filtfilt(numerator, denominator, samples)
        except ValueError as exc:
            raise FilterDesignError("Zero-phase IIR filtering failed.") from exc
    else:
        filtered = lfilter(numerator, denominator, samples)

    return Signal(
        samples=filtered,
        sampling_rate=rate,
        start_time=start_time,
        name=name,
        metadata={
            "filter_type": "iir",
            "zero_phase": zero_phase,
            "numerator": numerator.tolist(),
            "denominator": denominator.tolist(),
        },
    )
