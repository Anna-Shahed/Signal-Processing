from .event import Event
from .result import AnalysisResult
from .signal import Signal
from .spectrogram import Spectrogram
from .spectrum import Spectrum

__all__ = [
    "AnalysisResult",
    "Event",
    "Signal",
    "Spectrogram",
    "Spectrum",
]
class SignalIOError(Exception):
    """Raised when a signal cannot be read from or written to a file."""

