"""Signal data-model: time axis, statistics, validation, arithmetic, slicing."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing import Signal, SignalValidationError


def test_time_axis_and_duration():
    sig = Signal(np.zeros(100), sampling_rate=100, start_time=1.0, name="t")
    assert sig.n_samples == 100
    assert sig.duration == pytest.approx(1.0)
    assert sig.time[0] == pytest.approx(1.0)
    assert sig.time[-1] == pytest.approx(1.99)
    assert np.allclose(np.diff(sig.time), 0.01)


def test_statistics_on_known_values():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    sig = Signal(x, sampling_rate=100)
    assert sig.mean == pytest.approx(2.5)
    assert sig.rms == pytest.approx(np.sqrt(np.mean(x**2)))
    assert sig.variance == pytest.approx(np.var(x))
    assert sig.std == pytest.approx(np.std(x))
    assert sig.peak_amplitude == pytest.approx(4.0)


def test_normalize_peak():
    sig = Signal(np.array([-2.0, 1.0, 3.0]), sampling_rate=100)
    norm = sig.normalize()
    assert np.max(np.abs(norm.samples)) == pytest.approx(1.0)
    assert norm.sampling_rate == sig.sampling_rate


def test_slicing_preserves_sampling_rate():
    sig = Signal(np.arange(100.0), sampling_rate=50)
    part = sig[10:30]
    assert part.n_samples == 20
    assert part.sampling_rate == 50
    assert part.time[0] == pytest.approx(10 / 50)


def test_arithmetic():
    a = Signal(np.array([1.0, 2.0]), sampling_rate=100)
    b = Signal(np.array([3.0, 4.0]), sampling_rate=100)
    c = a + b
    assert np.allclose(c.samples, [4.0, 6.0])
    d = a * 2.0
    assert np.allclose(d.samples, [2.0, 4.0])


def test_serialization_roundtrip():
    sig = Signal(np.array([1.0, 2.0, 3.0]), sampling_rate=250,
                 name="tone", units="V", metadata={"origin": "test"})
    data = sig.to_dict()
    back = Signal.from_dict(data)
    assert np.allclose(back.samples, sig.samples)
    assert back.sampling_rate == 250
    assert back.name == "tone"
    assert back.units == "V"
    assert back.metadata == {"origin": "test"}


@pytest.mark.parametrize(
    "samples,fs",
    [
        (np.zeros(4), 0.0),
        (np.zeros(4), -10.0),
        (np.array([1.0, np.nan]), 100.0),
        (np.array([1.0, np.inf]), 100.0),
        (np.array([]), 100.0),
    ],
)
def test_validation_rejects_bad_inputs(samples, fs):
    with pytest.raises(SignalValidationError):
        Signal(samples, sampling_rate=fs)
