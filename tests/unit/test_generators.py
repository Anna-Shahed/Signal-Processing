"""Signal generators: length, amplitude, determinism, and chirp law."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.signal import hilbert

from signal_processing.generators import (
    chirp,
    composite,
    cosine,
    gaussian_noise,
    sine,
    white_noise,
)


def test_sine_length_and_amplitude():
    sig = sine(100.0, amplitude=2.0, duration=1.5, sampling_rate=1_000)
    assert sig.n_samples == 1_500
    assert np.max(np.abs(sig.samples)) == pytest.approx(2.0, abs=1e-3)


def test_sine_matches_numpy_reference():
    t = np.arange(1_000) / 1_000
    expected = 1.0 * np.sin(2 * np.pi * 50 * t)
    sig = sine(50.0, amplitude=1.0, phase=0.0, duration=1.0, sampling_rate=1_000)
    assert np.allclose(sig.samples, expected, atol=1e-12)


def test_cosine_phase_relation():
    s = sine(50.0, amplitude=1.0, duration=1.0, sampling_rate=1_000)
    c = cosine(50.0, amplitude=1.0, duration=1.0, sampling_rate=1_000)
    # cos(x) = sin(x + pi/2)
    s_shifted = sine(50.0, amplitude=1.0, phase=np.pi / 2, duration=1.0,
                     sampling_rate=1_000)
    assert np.allclose(c.samples, s_shifted.samples, atol=1e-12)
    assert np.allclose(c.samples, s.samples, atol=1e-12) is False


def test_chirp_instantaneous_frequency_linear():
    fs = 8_000
    sig = chirp(100.0, 5_000.0, 1.0, fs, kind="linear", amplitude=1.0)
    analytic = hilbert(sig.samples)
    inst = np.diff(np.unwrap(np.angle(analytic))) / (2 * np.pi) * fs
    # Edges of the chirp (ignore a few samples of filter transient).
    assert abs(inst[50] - 100.0) < 40.0
    assert abs(inst[-50] - 5_000.0) < 150.0


def test_white_noise_deterministic_with_seed():
    a = white_noise(1.0, 1_000, amplitude=0.5, seed=42)
    b = white_noise(1.0, 1_000, amplitude=0.5, seed=42)
    c = white_noise(1.0, 1_000, amplitude=0.5, seed=1)
    assert np.array_equal(a.samples, b.samples)
    assert not np.array_equal(a.samples, c.samples)


def test_white_noise_zero_mean_and_bounds():
    sig = white_noise(2.0, 4_000, amplitude=0.1, seed=3)
    assert sig.samples.mean() == pytest.approx(0.0, abs=0.02)
    assert np.max(np.abs(sig.samples)) <= 0.5  # loose bound on 0.1 amplitude


def test_gaussian_noise_std():
    sig = gaussian_noise(2.0, 4_000, amplitude=1.0, std=1.0, seed=5)
    assert np.std(sig.samples) == pytest.approx(1.0, abs=0.1)


def test_composite_sums_components():
    a = sine(10.0, amplitude=1.0, duration=1.0, sampling_rate=1_000)
    b = sine(20.0, amplitude=0.5, duration=1.0, sampling_rate=1_000)
    c = composite(a, b)
    assert np.allclose(c.samples, a.samples + b.samples)
    assert c.sampling_rate == a.sampling_rate
