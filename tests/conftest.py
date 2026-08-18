"""Shared fixtures for the test-suite (deterministic, no uncontrolled randomness)."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing import Signal
from signal_processing.generators import composite, sine, white_noise


@pytest.fixture(scope="session")
def sine_440() -> Signal:
    """1 s, 440 Hz tone at 8 kHz — bin resolution is exactly 1 Hz."""
    return sine(440.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)


@pytest.fixture(scope="session")
def noisy_tone() -> Signal:
    """50 Hz tone + white noise; SNR ~ 17 dB."""
    tone = sine(50.0, amplitude=1.0, duration=2.0, sampling_rate=2_000)
    noise = white_noise(2.0, 2_000, amplitude=0.1, seed=7)
    return composite(tone, noise)


@pytest.fixture(scope="session")
def burst_signal() -> Signal:
    """Two clean 50 Hz bursts (indices 100:200 and 500:600) for event tests."""
    fs = 1_000
    t = np.arange(fs) / fs
    x = np.zeros(fs)
    x[100:200] = np.sin(2 * np.pi * 50 * t[100:200])
    x[500:600] = np.sin(2 * np.pi * 50 * t[500:600])
    return Signal(x, sampling_rate=fs, name="bursts")
