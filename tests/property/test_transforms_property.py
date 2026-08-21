"""Property-based checks: transforms agree with NumPy references."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays

from signal_processing.transforms.dft import dft, idft
from signal_processing.transforms.fft import fft_radix2_educational

pytestmark = pytest.mark.property

finite = st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False)
array_strategy = arrays(np.float64, st.integers(1, 64), elements=finite)


@settings(max_examples=50, deadline=None)
@given(array_strategy)
def test_dft_matches_numpy_for_any_array(x):
    assert np.allclose(dft(x), np.fft.fft(x), atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(array_strategy)
def test_idft_inverts_dft_for_any_array(x):
    assert np.allclose(idft(dft(x)), x, atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(st.sampled_from([2, 4, 8, 16, 32, 64, 128, 256]))
def test_fft_radix2_matches_numpy_for_power_of_two(n):
    x = np.random.default_rng(0).standard_normal(n)
    assert np.allclose(fft_radix2_educational(x), np.fft.fft(x), atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(array_strategy)
def test_dft_and_fft_agree_for_any_array(x):
    if x.size not in {2, 4, 8, 16, 32, 64}:
        return
    assert np.allclose(dft(x), fft_radix2_educational(x), atol=1e-8)
