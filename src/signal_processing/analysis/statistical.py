"""Statistical descriptors of sampled signals."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import kurtosis, skew

from ..core import AnalysisResult, Signal
from ..utils.validation import SignalValidationError


def _as_1d(
    signal: Signal | np.ndarray,
    sampling_rate: float | None,
) -> tuple[np.ndarray, float]:
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
        rate = signal.sampling_rate
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when analyzing a plain array."
            )
        rate = float(sampling_rate)

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")
    return samples, rate


def mean(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the arithmetic mean."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(np.mean(samples))


def median(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the median."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(np.median(samples))


def variance(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    ddof: int = 0,
) -> float:
    """Return the population (``ddof=0``) or sample (``ddof=1``) variance."""
    samples, _ = _as_1d(signal, sampling_rate)
    if ddof not in (0, 1):
        raise SignalValidationError("ddof must be 0 (population) or 1 (sample).")
    return float(np.var(samples, ddof=ddof))


def standard_deviation(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    ddof: int = 0,
) -> float:
    """Return the standard deviation."""
    samples, _ = _as_1d(signal, sampling_rate)
    if ddof not in (0, 1):
        raise SignalValidationError("ddof must be 0 (population) or 1 (sample).")
    return float(np.std(samples, ddof=ddof))


def rms(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the root-mean-square amplitude."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(np.sqrt(np.mean(np.square(samples))))


def peak_to_peak(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the difference between the maximum and minimum samples."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(np.max(samples) - np.min(samples))


def crest_factor(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return peak-to-RMS ratio, a measure of signal spikiness."""
    samples, _ = _as_1d(signal, sampling_rate)
    value = float(np.max(np.abs(samples)))
    energy = float(np.mean(np.square(samples)))
    if energy == 0:
        raise SignalValidationError("Crest factor is undefined for a zero signal.")
    return value / np.sqrt(energy)


def skewness(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    bias: bool = True,
) -> float:
    """Return the sample skewness."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(skew(samples, bias=bias))


def kurtosis(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    fisher: bool = True,
    bias: bool = True,
) -> float:
    """Return the kurtosis (Fisher excess by default)."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(kurtosis(samples, fisher=fisher, bias=bias))


def energy(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the total energy (sum of squared samples)."""
    samples, _ = _as_1d(signal, sampling_rate)
    return float(np.sum(np.square(samples)))


def signal_to_noise_ratio(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    noise: Signal | np.ndarray | None = None,
    reference: float | None = None,
) -> float:
    """Return the SNR in decibels.

    Either a noise signal is supplied and the clean signal is estimated by
    subtraction, or a reference clean-signal power is supplied directly.
    """
    samples, _ = _as_1d(signal, sampling_rate)

    if reference is not None:
        clean_power = float(reference) ** 2
        noise_power = float(np.mean(np.square(samples)))
    elif noise is not None:
        noise_samples = np.asarray(noise, dtype=float)
        if noise_samples.shape != samples.shape:
            raise SignalValidationError(
                "The noise signal must match the analyzed signal's shape."
            )
        clean_estimate = samples - noise_samples
        clean_power = float(np.mean(np.square(clean_estimate)))
        noise_power = float(np.mean(np.square(noise_samples)))
    else:
        raise SignalValidationError(
            "SNR requires either a noise signal or a reference amplitude."
        )

    if clean_power <= 0 or noise_power <= 0:
        raise SignalValidationError("SNR is undefined for zero clean or noise power.")

    return 10.0 * np.log10(clean_power / noise_power)


def analyze_statistical(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    noise: Signal | np.ndarray | None = None,
) -> AnalysisResult:
    """Compute the full statistical descriptor set."""
    input_signal = _as_1d(signal, sampling_rate)[0]
    result = AnalysisResult(
        metrics={
            "mean": mean(input_signal),
            "median": median(input_signal),
            "variance": variance(input_signal),
            "standard_deviation": standard_deviation(input_signal),
            "rms": rms(input_signal),
            "peak_amplitude": float(np.max(np.abs(input_signal))),
            "peak_to_peak": peak_to_peak(input_signal),
            "crest_factor": crest_factor(input_signal),
            "skewness": skewness(input_signal),
            "kurtosis": kurtosis(input_signal),
            "energy": energy(input_signal),
        },
        metadata={
            "feature": "statistical",
            "n_samples": input_signal.size,
        },
    )

    try:
        result.metrics["snr_db"] = signal_to_noise_ratio(
            input_signal, noise=noise
        )
    except SignalValidationError:
        pass

    return result
