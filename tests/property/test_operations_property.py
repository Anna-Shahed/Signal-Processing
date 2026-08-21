"""Property-based checks: convolution/correlation agree with references."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays

from fixtures import reference_circular_convolution
from signal_processing.operations import (
    convolve,
    convolve_circular,
    convolve_fft,
)

pytestmark = pytest.mark.property

finite = st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False)
array_strategy = arrays(np.float64, st.integers(1, 40), elements=finite)


@settings(max_examples=50, deadline=None)
@given(array_strategy, array_strategy)
def test_convolve_matches_numpy(a, b):
    assert np.allclose(convolve(a, b, mode="full"), np.convolve(a, b, mode="full"), atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(array_strategy, array_strategy)
def test_convolve_fft_matches_numpy(a, b):
    assert np.allclose(convolve_fft(a, b, mode="full"), np.convolve(a, b, mode="full"), atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(array_strategy, array_strategy)
def test_circular_convolution_matches_reference(a, b):
    assert np.allclose(convolve_circular(a, b), reference_circular_convolution(a, b), atol=1e-8)


@settings(max_examples=50, deadline=None)
@given(array_strategy)
def test_convolve_with_impulse_is_identity(x):
    impulse = np.array([1.0])
    assert np.allclose(convolve(x, impulse, mode="full")[: x.size], x, atol=1e-8)
