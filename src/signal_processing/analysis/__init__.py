"""Analysis public API."""

from .anomaly import (
    energy_anomalies,
    robust_threshold_anomalies,
    rolling_anomalies,
    zscore_anomalies,
)
from .events import (
    adaptive_threshold_events,
    peak_events,
    threshold_events,
)
from .features import envelope, extract_features, zero_crossing_rate
from .peaks import Peak, detect_peaks, peaks_to_events
from .spectral import (
    analyze_spectral,
    dominant_frequency,
    magnitude_spectrum,
    power_spectrum,
    spectral_bandwidth,
    spectral_centroid,
    spectral_entropy,
    spectral_flatness,
    spectral_rolloff,
)
from .statistical import (
    analyze_statistical,
    crest_factor,
    energy,
    kurtosis,
    mean,
    median,
    peak_to_peak,
    rms,
    signal_to_noise_ratio,
    skewness,
    standard_deviation,
    variance,
)


def analyze(
    signal: Signal | object,
    *,
    sampling_rate: float | None = None,
) -> object:
    """Run the combined statistical and spectral analysis pipeline."""
    return extract_features(signal, sampling_rate=sampling_rate)


__all__ = [
    "Peak",
    "adaptive_threshold_events",
    "analyze",
    "analyze_spectral",
    "analyze_statistical",
    "crest_factor",
    "detect_peaks",
    "dominant_frequency",
    "energy",
    "energy_anomalies",
    "envelope",
    "extract_features",
    "kurtosis",
    "magnitude_spectrum",
    "mean",
    "median",
    "peak_events",
    "peak_to_peak",
    "peaks_to_events",
    "power_spectrum",
    "rms",
    "robust_threshold_anomalies",
    "rolling_anomalies",
    "signal_to_noise_ratio",
    "skewness",
    "spectral_bandwidth",
    "spectral_centroid",
    "spectral_entropy",
    "spectral_flatness",
    "spectral_rolloff",
    "standard_deviation",
    "threshold_events",
    "variance",
    "zero_crossing_rate",
    "zscore_anomalies",
]
