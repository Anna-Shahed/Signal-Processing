"""STFT/ISTFT shapes and perfect reconstruction; Haar round-trip."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing.transforms.stft import istft, stft
from signal_processing.transforms.wavelet import dwt, idwt


def test_stft_one_sided_shape(sine_440):
    spec = stft(sine_440, nperseg=256, hop_length=128, window="hann")
    assert spec.frequencies.size == 256 // 2 + 1
    assert spec.times.size > 1
    assert spec.sampling_rate == pytest.approx(8_000)
    # Time resolution equals hop/fs.
    assert spec.times[1] - spec.times[0] == pytest.approx(128 / 8_000)


def test_stft_time_frequency_extent(sine_440):
    spec = stft(sine_440, nperseg=256, hop_length=128, window="hann")
    assert spec.times[0] >= 0.0
    assert spec.times[-1] <= 1.0
    assert spec.frequencies[0] == 0.0
    assert spec.frequencies[-1] <= 4_000.0  # Nyquist


def test_istft_reconstruction_hann_50(sine_440):
    x = sine_440.samples
    spec = stft(x, nperseg=256, hop_length=128, window="hann")
    y = istft(spec)
    assert y.size >= x.size
    assert np.allclose(y[: x.size], x, atol=1e-4)


def test_haar_dwt_idwt_roundtrip(sine_440):
    x = sine_440.samples[:256]
    coeffs = dwt(x, wavelet="haar", level=1)
    y = idwt(coeffs, wavelet="haar")
    assert np.allclose(y[: x.size], x, atol=1e-8)
