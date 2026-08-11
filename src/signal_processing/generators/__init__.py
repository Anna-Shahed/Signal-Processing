"""Signal-generation public API."""

from .chirp import linear_chirp, logarithmic_chirp, quadratic_chirp
from .composite import composite, mix
from .noise import gaussian_noise, pink_noise, uniform_noise, white_noise
from .sinusoidal import cosine, sine
from .waveforms import sawtooth, square, triangle

__all__ = [
    "composite",
    "cosine",
    "gaussian_noise",
    "linear_chirp",
    "logarithmic_chirp",
    "mix",
    "pink_noise",
    "quadratic_chirp",
    "sawtooth",
    "sine",
    "square",
    "triangle",
    "uniform_noise",
    "white_noise",
]
