"""Convolution, correlation, and resampling against references."""

from __future__ import annotations

import numpy as np
import pytest

from fixtures import reference_circular_convolution
from signal_processing.generators import sine
from signal_processing.operations import (
    autocorrelation,
    convolve,
    convolve_circular,
    convolve_fft,
    cross_correlation,
    downsample,
    normalized_cross_correlation,
    resample,
    upsample,
)


@pytest.mark.parametrize("mode", ["full", "same", "valid"])
def test_convolve_matches_numpy(mode):
    rng = np.random.default_rng(0)
    a = rng.standard_normal(9)
    b = rng.standard_normal(5)
    assert np.allclose(convolve(a, b, mode=mode), np.convolve(a, b, mode=mode), atol=1e-10)


def test_convolve_fft_matches_numpy():
    rng = np.random.default_rng(1)
    a = rng.standard_normal(32)
    b = rng.standard_normal(12)
    assert np.allclose(convolve_fft(a, b, mode="full"), np.convolve(a, b, mode="full"), atol=1e-10)


def test_convolve_and_fft_agree():
    rng = np.random.default_rng(2)
    a = rng.standard_normal(64)
    b = rng.standard_normal(20)
    assert np.allclose(convolve(a, b, mode="full"), convolve_fft(a, b, mode="full"), atol=1e-9)


def test_circular_convolution_matches_reference():
    rng = np.random.default_rng(3)
    a = rng.standard_normal(8)
    b = rng.standard_normal(6)
    assert np.allclose(convolve_circular(a, b), reference_circular_convolution(a, b), atol=1e-10)


def test_autocorrelation_zero_lag_is_energy():
    x = np.array([1.0, 2.0, 3.0])
    values, lags = autocorrelation(x)
    idx = int(np.where(lags == 0)[0][0])
    assert values[idx] == pytest.approx(np.sum(x**2))


def test_cross_correlation_lag_zero_known():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([0.0, 1.0, 0.5])
    values, lags = cross_correlation(a, b)
    idx = int(np.where(lags == 0)[0][0])
    assert values[idx] == pytest.approx(1 * 0 + 2 * 1 + 3 * 0.5)


def test_normalized_correlation_identical_is_one():
    rng = np.random.default_rng(4)
    x = rng.standard_normal(50)
    values, _ = normalized_cross_correlation(x, x)
    assert np.max(np.abs(values)) == pytest.approx(1.0, abs=1e-9)


def test_resample_output_length():
    rng = np.random.default_rng(5)
    x = rng.standard_normal(100)
    assert resample(x, 250).size == 250
    assert resample(x, 50).size == 50


def test_resample_preserves_low_frequency_tone():
    sig = sine(20.0, amplitude=1.0, duration=1.0, sampling_rate=1_000)
    y = resample(sig.samples, 500)
    assert y.size == 500
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(np.abs(np.fft.rfft(y * np.hanning(500))))
    freqs = np.fft.rfftfreq(500, d=1 / 500)
    assert abs(freqs[peaks[0]] - 20.0) < 5.0


def test_downsample_upsample_lengths():
    x = np.arange(100.0)
    assert downsample(x, 4).size == 25
    assert upsample(x, 2).size == 200
