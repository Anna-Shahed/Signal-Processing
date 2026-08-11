"""Spectral feature extraction."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..core import AnalysisResult, Signal, Spectrum
from ..transforms.fft import fft, frequency_bins
from ..utils.validation import SignalValidationError, validate_sampling_rate
from ..filters.windows import get_window


def _as_signal(
    signal: Signal | np.ndarray,
    sampling_rate: float | None,
) -> Signal:
    if isinstance(signal, Signal):
        return signal
    samples = np.asarray(signal, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if sampling_rate is None:
        raise SignalValidationError(
            "sampling_rate is required when analyzing a plain array."
        )
    return Signal(samples=samples, sampling_rate=sampling_rate)


def magnitude_spectrum(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
    scale: bool = True,
) -> Spectrum:
    """Return a one-sided magnitude spectrum with optional windowing.

    When ``scale=True`` the Hann-windowed spectrum is normalized by the
    window's coherent gain (mean), so a sinusoidal component has a peak close
    to its true amplitude.
    """
    input_signal = _as_signal(signal, sampling_rate)
    samples = input_signal.samples

    if window is None:
        analysis_samples = samples
        gain = 1.0
    else:
        values = get_window(window, samples.size)
        analysis_samples = samples * values
        gain = float(np.mean(values)) if scale else 1.0

    spectrum = fft(
        analysis_samples,
        sampling_rate=input_signal.sampling_rate,
        n=n,
        one_sided=True,
    )
    if scale and gain > 0:
        spectrum.values = spectrum.values / gain

    spectrum.metadata["feature"] = "magnitude_spectrum"
    spectrum.metadata["window"] = None if window is None else window
    return spectrum


def power_spectrum(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> Spectrum:
    """Return a one-sided power spectrum."""
    spectrum = magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    )
    spectrum.values = spectrum.power.astype(complex)
    spectrum.metadata["feature"] = "power_spectrum"
    return spectrum


def dominant_frequency(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> float:
    """Return the frequency of the largest spectral peak."""
    return magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    ).dominant_frequency


def spectral_centroid(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> float:
    """Return the magnitude-weighted mean frequency."""
    return magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    ).spectral_centroid


def spectral_bandwidth(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> float:
    """Return the magnitude-weighted frequency spread."""
    return magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    ).bandwidth


def spectral_rolloff(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
    fraction: float = 0.85,
) -> float:
    """Return the frequency below which ``fraction`` of the power lies."""
    fraction = float(fraction)
    if not 0.0 < fraction <= 1.0:
        raise SignalValidationError("fraction must be in (0, 1].")

    spectrum = magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    )
    power = spectrum.power
    total = float(np.sum(power))
    if total == 0:
        return 0.0
    cumulative = np.cumsum(power) / total
    index = int(np.searchsorted(cumulative, fraction))
    return float(spectrum.frequencies[min(index, spectrum.frequencies.size - 1)])


def spectral_flatness(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> float:
    """Return the ratio of geometric to arithmetic mean power (0 to 1)."""
    spectrum = magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    )
    power = spectrum.power[1:]  # exclude DC, which can be zero
    arithmetic = float(np.mean(power))
    if arithmetic == 0:
        return 0.0
    geometric = float(np.exp(np.mean(np.log(power + np.finfo(float).tiny))))
    return float(np.clip(geometric / arithmetic, 0.0, 1.0))


def spectral_entropy(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> float:
    """Return the Shannon entropy of the normalized power distribution."""
    spectrum = magnitude_spectrum(
        signal,
        sampling_rate=sampling_rate,
        n=n,
        window=window,
    )
    power = spectrum.power
    total = float(np.sum(power))
    if total == 0:
        return 0.0
    probabilities = power / total
    probabilities = probabilities[probabilities > 0]
    return float(-np.sum(probabilities * np.log2(probabilities)))


def zero_crossing_rate(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
) -> float:
    """Return the fraction of sample transitions across zero."""
    input_signal = _as_signal(signal, sampling_rate)
    samples = input_signal.samples
    if samples.size < 2:
        return 0.0
    crossings = np.count_nonzero(np.diff(np.signbit(samples)))
    return float(crossings / (samples.size - 1))


def analyze_spectral(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    n: int | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
) -> AnalysisResult:
    """Compute the full spectral feature set as an :class:`AnalysisResult`."""
    input_signal = _as_signal(signal, sampling_rate)
    spectrum = magnitude_spectrum(
        input_signal,
        sampling_rate=input_signal.sampling_rate,
        n=n,
        window=window,
    )
    return AnalysisResult(
        metrics={
            "dominant_frequency": spectrum.dominant_frequency,
            "dominant_magnitude": float(np.max(spectrum.magnitude)),
            "spectral_centroid": spectrum.spectral_centroid,
            "spectral_bandwidth": spectrum.bandwidth,
            "spectral_rolloff_85": spectral_rolloff(input_signal, window=window),
            "spectral_flatness": spectral_flatness(input_signal, window=window),
            "spectral_entropy_bits": spectral_entropy(input_signal, window=window),
            "zero_crossing_rate": zero_crossing_rate(input_signal),
        },
        arrays={
            "frequencies": spectrum.frequencies,
            "magnitude": spectrum.magnitude,
            "phase": spectrum.phase,
            "power": spectrum.power,
        },
        metadata={
            "feature": "spectral",
            "sampling_rate": input_signal.sampling_rate,
            "n_samples": input_signal.n_samples,
        },
    )
