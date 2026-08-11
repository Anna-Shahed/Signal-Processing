"""Power spectral density estimation."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import welch as scipy_welch

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


def periodogram(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    window: str | tuple[str, float] | np.ndarray | None = "hann",
    nfft: int | None = None,
    scaling: str = "density",
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a one-sided periodogram PSD estimate.

    Returns ``(frequencies, psd)`` with units of amplitude squared per hertz
    for ``scaling='density'`` or squared amplitude per bin for ``'spectrum'``.
    """
    samples, rate = _as_1d(signal, sampling_rate)
    if scaling not in {"density", "spectrum"}:
        raise SignalValidationError("scaling must be 'density' or 'spectrum'.")

    if window is None:
        analysis_samples = samples
    else:
        from ..filters.windows import get_window

        values = get_window(window, samples.size)
        analysis_samples = samples * values

    frequencies, density = scipy_welch(
        analysis_samples,
        fs=rate,
        nperseg=samples.size,
        noverlap=0,
        nfft=nfft,
        window=window,
        scaling="density",
    )
    if scaling == "spectrum":
        density = density * rate / samples.size
    return frequencies, density


def welch(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    nperseg: int | None = None,
    noverlap: int | None = None,
    nfft: int | None = None,
    window: str | tuple[str, float] | np.ndarray = "hann",
    scaling: str = "density",
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a Welch-averaged PSD estimate.

    Returns ``(frequencies, psd)``. Averaging over overlapping segments
    reduces estimator variance at the cost of frequency resolution.
    """
    samples, rate = _as_1d(signal, sampling_rate)
    if scaling not in {"density", "spectrum"}:
        raise SignalValidationError("scaling must be 'density' or 'spectrum'.")

    frequencies, density = scipy_welch(
        samples,
        fs=rate,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
        window=window,
        scaling="density",
    )
    if scaling == "spectrum":
        density = density * rate / (nperseg if nperseg is not None else samples.size)
    return frequencies, density


def estimate_psd(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    method: str = "welch",
    nperseg: int | None = None,
    window: str | tuple[str, float] | np.ndarray = "hann",
) -> AnalysisResult:
    """Return a structured PSD analysis result."""
    if method not in {"periodogram", "welch"}:
        raise SignalValidationError("method must be 'periodogram' or 'welch'.")

    samples, rate = _as_1d(signal, sampling_rate)
    if method == "periodogram":
        frequencies, density = periodogram(
            samples,
            sampling_rate=rate,
            window=window,
        )
    else:
        frequencies, density = welch(
            samples,
            sampling_rate=rate,
            nperseg=nperseg,
            window=window,
        )

    return AnalysisResult(
        metrics={
            "total_power": float(np.trapezoid(density, frequencies)),
            "peak_psd_frequency": float(frequencies[int(np.argmax(density))]),
        },
        arrays={"frequencies": frequencies, "psd": density},
        metadata={"method": method, "sampling_rate": rate},
    )
