"""Signal Processing Laboratory public package API."""

from .__version__ import __version__
from .core import AnalysisResult, Event, Signal, Spectrogram, Spectrum
from .utils import (
    FilterDesignError,
    PipelineError,
    SignalIOError,
    SignalProcessingError,
    SignalValidationError,
    TransformError,
)

__all__ = [
    "AnalysisResult",
    "Event",
    "FilterDesignError",
    "PipelineError",
    "Signal",
    "SignalIOError",
    "SignalProcessingError",
    "SignalValidationError",
    "Spectrogram",
    "Spectrum",
    "TransformError",
    "__version__",
]
