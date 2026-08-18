"""Statistical and spectral analysis: known values and sanity checks."""

from __future__ import annotations

import numpy as np
import pytest

from fixtures import reference_snr_db
from signal_processing import Signal
from signal_processing.analysis import analyze
from signal_processing.analysis.spectral import magnitude_spectrum
from signal_processing.generators import composite, sine, white_noise


def test_analyze_metrics_keys(sine_440):
    result = analyze(sine_440)
    for key in ["mean", "median", "variance", "std", "rms", "peak_to_peak",
                "crest_factor", "skewness", "kurtosis", "energy",
                "snr_db", "dominant_frequency", "zero_crossing_rate"]:
        assert key in result.metrics, f"missing metric: {key}"


def test_analyze_known_statistics():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    sig = Signal(x, sampling_rate=100)
    result = analyze(sig)
    assert result.metrics["mean"] == pytest.approx(2.5)
    assert result.metrics["rms"] == pytest.approx(np.sqrt(np.mean(x**2)))
    assert result.metrics["peak_to_peak"] == pytest.approx(3.0)
    assert result.metrics["energy"] == pytest.approx(np.sum(x**2))


def test_analyze_snr_matches_reference(noisy_tone):
    result = analyze(noisy_tone)
    assert result.metrics["snr_db"] == pytest.approx(reference_snr_db(50.0, 0.1), abs=1.5)


def test_amplitude_corrected_peak(sine_440):
    spec = magnitude_spectrum(sine_440, window="hann")
    peak = float(np.max(np.abs(spec.values)))
    assert peak == pytest.approx(1.0, rel=0.05)  # coherent-gain corrected


def test_spectral_flatness_tone_low_noise_high():
    tone = sine(200.0, amplitude=1.0, duration=1.0, sampling_rate=4_000)
    noise = white_noise(1.0, 4_000, amplitude=1.0, seed=9)
    from signal_processing.analysis.spectral import spectral_flatness
    assert spectral_flatness(tone) < 0.5
    assert spectral_flatness(noise) > 0.01


def test_zero_crossing_rate_of_tone():
    sig = sine(50.0, amplitude=1.0, duration=1.0, sampling_rate=1_000)
    from signal_processing.analysis.spectral import zero_crossing_rate
    zcr = zero_crossing_rate(sig)
    assert zcr == pytest.approx(2 * 50 / 1_000, abs=0.02)


def test_analyze_result_serialization(sine_440):
    result = analyze(sine_440)
    data = result.to_dict()
    assert "metrics" in data
    assert "arrays" in data or "metadata" in data
    assert isinstance(result.summary(), str) and len(result.summary()) > 0
