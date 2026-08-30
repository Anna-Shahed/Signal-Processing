from __future__ import annotations

import importlib
import pkgutil
from typing import Any

import numpy as np
from scipy import stats as _scipy_stats

from ..core import AnalysisResult, Signal
from ..utils.validation import SignalValidationError

__all__ = ["analyze"]


def analyze(
    signal: Signal | np.ndarray,
    sampling_rate: float | None = None,
) -> AnalysisResult:
    """Compute the standard metric set: statistics + dominant frequency + SNR."""
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
        rate = float(signal.sampling_rate)
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when analyzing a plain array."
            )
        rate = float(sampling_rate)

    mean = float(np.mean(samples))
    std = float(np.std(samples))
    variance = float(np.var(samples))
    rms = float(np.sqrt(np.mean(samples**2)))
    peak = float(np.max(np.abs(samples)))
    peak_to_peak = float(np.max(samples) - np.min(samples))
    crest_factor = float(peak / rms) if rms > 0 else 0.0
    energy = float(np.sum(samples**2))
    skewness = float(_scipy_stats.skew(samples))
    kurtosis = float(_scipy_stats.kurtosis(samples))

    dominant_frequency = 0.0
    snr_db = 0.0
    try:
        from .spectral import magnitude_spectrum

        spec = magnitude_spectrum(Signal(samples, sampling_rate=rate))
        mags = np.asarray(np.abs(getattr(spec, "values", None) or spec))
        freqs = getattr(spec, "frequencies", None)
        if freqs is None:
            freqs = np.arange(mags.size) * rate / max(mags.size, 1)
        freqs = np.asarray(freqs)
        peak_idx = int(np.argmax(mags))
        dominant_frequency = float(freqs[peak_idx])
        positive = mags[mags > 0]
        noise_floor = float(np.median(positive)) if positive.size else 1e-12
        snr_db = float(20 * np.log10(mags[peak_idx] / (noise_floor + 1e-12) + 1e-12))
    except Exception:
        pass

    return AnalysisResult(
        metrics={
            "mean": mean,
            "std": std,
            "variance": variance,
            "rms": rms,
            "peak": peak,
            "peak_to_peak": peak_to_peak,
            "crest_factor": crest_factor,
            "energy": energy,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "dominant_frequency": dominant_frequency,
            "snr_db": snr_db,
        },
        metadata={"feature": "analyze"},
    )


_CACHE: dict[str, Any] = {}

def __getattr__(name: str) -> Any:
  
    if name in _CACHE:
        return _CACHE[name]
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    for info in pkgutil.iter_modules(__path__):
        try:
            module = importlib.import_module(f"{__name__}.{info.name}")
        except Exception:
            continue
        attr = getattr(module, name, None)
        if attr is not None:
            _CACHE[name] = attr
            return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
