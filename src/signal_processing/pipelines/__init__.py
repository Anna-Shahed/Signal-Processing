"""Pipeline public API."""

from .pipeline import Pipeline
from .stages import (
    detrend,
    fft_stage,
    highpass,
    lowpass,
    normalize,
    peak_detection,
)

__all__ = [
    "Pipeline",
    "detrend",
    "fft_stage",
    "highpass",
    "lowpass",
    "normalize",
    "peak_detection",
]
