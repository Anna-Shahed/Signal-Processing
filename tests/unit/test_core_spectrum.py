"""Spectrum data-model and FFT wrapper behaviour."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing import Signal
from signal_processing.transforms import fft


def test_fft_returns_spectrum(sine_440):
    spec = fft(sine_440, one_sided=True)
    assert spec.sampling_rate == pytest.approx(8_000)
    assert spec.frequencies.ndim == 1
    assert spec.values.dtype == np.complex128


def test_one_sided_vs_two_sided_shapes(sine_440):
    n = sine_440.n_samples
    one = fft(sine_440, one_sided=True)
    two = fft(sine_440, one_sided=False)
    assert one.frequencies.size == n // 2 + 1
    assert two.frequencies.size == n
    assert one.one_sided is True
    assert two.one_sided is False


def test_dominant_frequency_of_tone(sine_440):
    spec = fft(sine_440, one_sided=True)
    # 1 s at 8 kHz => 1 Hz bins; expect the peak within a couple of bins.
    assert abs(spec.dominant_frequency - 440.0) < 3.0


def test_magnitude_phase_power_consistency(sine_440):
    spec = fft(sine_440, one_sided=True)
    mag = spec.magnitude
    assert np.allclose(mag, np.abs(spec.values))
    assert np.allclose(spec.power, mag**2)
    assert np.allclose(spec.phase, np.angle(spec.values))


def test_centroid_sanity(sine_440):
    spec = fft(sine_440, one_sided=True)
    assert 300.0 < spec.spectral_centroid < 600.0
    assert spec.bandwidth > 0.0
