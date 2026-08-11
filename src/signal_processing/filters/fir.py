"""Finite impulse response filter design and application."""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.signal import firwin, lfilter, filtfilt

from ..core import Signal
from ..utils.validation import (
    FilterDesignError,
    SignalValidationError,
    validate_sampling_rate,
)
from .windows import get_window


def _validate_band(frequency: float, sampling_rate: float, label: str) -> float:
    frequency = float(frequency)
    nyquist = sampling_rate / 2.0

    if not np.isfinite(frequency) or frequency <= 0:
        raise FilterDesignError(f"{label} must be finite and greater than zero.")
    if frequency >= nyquist:
        raise FilterDesignError(f"{label} must be below the Nyquist frequency {nyquist} Hz.")
    return frequency


def _validate_band_edges(edges: tuple[float, float], sampling_rate: float) -> None:
    low, high = edges
    low = _validate_band(low, sampling_rate, "low cutoff")
    high = _validate_band(high, sampling_rate, "high cutoff")
    if low >= high:
        raise FilterDesignError("low cutoff must be below high cutoff.")


def _validate_order(order: int, numtaps: int) -> int:
    order = int(order)
    if order < 1:
        raise FilterDesignError("Filter order must be at least one.")
    if numtaps < 1:
        raise FilterDesignError("numtaps must be positive.")
    return order


def _signal_input(
    signal: Signal | np.ndarray,
    sampling_rate: float | None,
) -> tuple[np.ndarray, float]:
    if isinstance(signal, Signal):
        if signal.samples.ndim != 1:
            raise SignalValidationError("FIR filtering requires a one-dimensional signal.")
        return signal.samples.astype(float), signal.sampling_rate

    samples = np.asarray(signal, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if sampling_rate is None:
        raise SignalValidationError(
            "sampling_rate is required when filtering a plain array."
        )
    return samples, validate_sampling_rate(sampling_rate)


def design_lowpass(
    numtaps: int,
    cutoff: float,
    sampling_rate: float,
    *,
    window: str | tuple[str, float] | np.ndarray = "hamming",
    scale: bool = True,
) -> np.ndarray:
    """Design an FIR low-pass filter."""
    rate = validate_sampling_rate(sampling_rate)
    cutoff = _validate_band(cutoff, rate, "cutoff")
    numtaps = int(numtaps)
    if numtaps < 1:
        raise FilterDesignError("numtaps must be positive.")

    window_values = get_window(window, numtaps)
    return np.asarray(
        firwin(numtaps, cutoff, fs=rate, window=window_values, scale=scale),
        dtype=float,
    )


def design_highpass(
    numtaps: int,
    cutoff: float,
    sampling_rate: float,
    *,
    window: str | tuple[str, float] | np.ndarray = "hamming",
    scale: bool = True,
) -> np.ndarray:
    """Design an FIR high-pass filter."""
    rate = validate_sampling_rate(sampling_rate)
    cutoff = _validate_band(cutoff, rate, "cutoff")
    numtaps = int(numtaps)
    if numtaps < 1:
        raise FilterDesignError("numtaps must be positive.")

    window_values = get_window(window, numtaps)
    return np.asarray(
        firwin(numtaps, cutoff, fs=rate, window=window_values, pass_zero=False, scale=scale),
        dtype=float,
    )


def design_bandpass(
    numtaps: int,
    cutoff_low: float,
    cutoff_high: float,
    sampling_rate: float,
    *,
    window: str | tuple[str, float] | np.ndarray = "hamming",
    scale: bool = True,
) -> np.ndarray:
    """Design an FIR band-pass filter."""
    rate = validate_sampling_rate(sampling_rate)
    _validate_band_edges((cutoff_low, cutoff_high), rate)
    numtaps = int(numtaps)
    if numtaps < 1:
        raise FilterDesignError("numtaps must be positive.")

    window_values = get_window(window, numtaps)
    return np.asarray(
        firwin(
            numtaps,
            [cutoff_low, cutoff_high],
            fs=rate,
            window=window_values,
            pass_zero=False,
            scale=scale,
        ),
        dtype=float,
    )


def design_bandstop(
    numtaps: int,
    cutoff_low: float,
    cutoff_high: float,
    sampling_rate: float,
    *,
    window: str | tuple[str, float] | np.ndarray = "hamming",
    scale: bool = True,
) -> np.ndarray:
    """Design an FIR band-stop filter."""
    rate = validate_sampling_rate(sampling_rate)
    _validate_band_edges((cutoff_low, cutoff_high), rate)
    numtaps = int(numtaps)
    if numtaps < 1:
        raise FilterDesignError("numtaps must be positive.")

    window_values = get_window(window, numtaps)
    return np.asarray(
        firwin(
            numtaps,
            [cutoff_low, cutoff_high],
            fs=rate,
            window=window_values,
            pass_zero=True,
            scale=scale,
        ),
        dtype=float,
    )


def fir_filter(
    signal: Signal | np.ndarray,
    coefficients: np.ndarray,
    *,
    sampling_rate: float | None = None,
    zero_phase: bool = False,
    name: str = "fir_filtered",
) -> Signal:
    """Apply an FIR filter to a signal.

    With ``zero_phase=True`` the filter is applied in both directions using
    SciPy's forward-backward technique, which doubles the effective filter
    order and removes phase distortion at the cost of non-causality.
    """
    samples, rate = _signal_input(signal, sampling_rate)
    coefficients = np.asarray(coefficients, dtype=float)

    if coefficients.ndim != 1 or coefficients.size == 0:
        raise FilterDesignError("Filter coefficients must be a non-empty one-dimensional array.")

    if zero_phase:
        try:
            filtered = filtfilt(coefficients, [1.0], samples)
        except ValueError as exc:
            raise FilterDesignError("Zero-phase filtering failed.") from exc
    else:
        filtered = lfilter(coefficients, [1.0], samples)

    start_time = signal.start_time if isinstance(signal, Signal) else 0.0
    return Signal(
        samples=filtered,
        sampling_rate=rate,
        start_time=start_time,
        name=name,
        metadata={
            "filter_type": "fir",
            "zero_phase": zero_phase,
            "numtaps": coefficients.size,
            "coefficients": coefficients.tolist(),
        },
    )
