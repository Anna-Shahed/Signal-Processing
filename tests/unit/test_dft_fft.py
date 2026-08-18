"""Educational transforms: DFT vs NumPy, radix-2 FFT, round-trips."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing.transforms.dft import dft, idft
from signal_processing.transforms.fft import (
    fft_radix2_educational,
    ifft_radix2_educational,
)


@pytest.mark.parametrize("n", [8, 16, 32, 64])
def test_dft_matches_numpy(n):
    rng = np.random.default_rng(0)
    x = rng.standard_normal(n)
    assert np.allclose(dft(x), np.fft.fft(x), atol=1e-9)


@pytest.mark.parametrize("n", [8, 16, 32, 64])
def test_idft_inverts_dft(n):
    rng = np.random.default_rng(1)
    x = rng.standard_normal(n)
    assert np.allclose(idft(dft(x)), x, atol=1e-10)


@pytest.mark.parametrize("n", [2, 4, 8, 16, 32, 64, 128, 256])
def test_fft_radix2_matches_numpy(n):
    rng = np.random.default_rng(2)
    x = rng.standard_normal(n)
    assert np.allclose(fft_radix2_educational(x), np.fft.fft(x), atol=1e-9)


@pytest.mark.parametrize("n", [4, 8, 16, 32, 64, 128])
def test_ifft_radix2_roundtrip(n):
    rng = np.random.default_rng(3)
    x = rng.standard_normal(n)
    assert np.allclose(ifft_radix2_educational(fft_radix2_educational(x)), x, atol=1e-10)


def test_dft_and_fft_agree(sine_440):
    x = sine_440.samples[:128]
    assert np.allclose(dft(x), fft_radix2_educational(x), atol=1e-9)


def test_fft_preserves_energy_parseval():
    rng = np.random.default_rng(4)
    x = rng.standard_normal(64)
    X = fft_radix2_educational(x)
    assert np.sum(np.abs(X) ** 2) == pytest.approx(len(x) * np.sum(x**2))
