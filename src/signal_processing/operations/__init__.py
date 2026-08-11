"""Signal operations public API."""

from .convolution import circular_convolve, convolve, convolve_fft, direct_convolve
from .correlation import (
    autocorrelation,
    cross_correlation,
    normalized_cross_correlation,
)
from .normalization import normalize_peak, normalize_rms
from .resampling import downsample, resample, upsample
from .windowing import apply_window

__all__ = [
    "apply_window",
    "autocorrelation",
    "circular_convolve",
    "convolve",
    "convolve_fft",
    "cross_correlation",
    "direct_convolve",
    "downsample",
    "normalize_peak",
    "normalize_rms",
    "normalized_cross_correlation",
    "resample",
    "upsample",
]
