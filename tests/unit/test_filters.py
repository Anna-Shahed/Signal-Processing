"""FIR/IIR design and filtering: attenuation behaviour and invariants."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing.filters import (
    design_butterworth,
    design_highpass,
    design_lowpass,
    fir_filter,
    iir_filter,
)
from signal_processing.generators import sine


def test_fir_coefficients_symmetric():
    b = design_lowpass(65, 1_000, 8_000, window="hamming")
    assert len(b) == 65
    assert np.allclose(b, b[::-1], atol=1e-12)  # linear phase


def test_lowpass_keeps_passband_attenuates_stopband():
    fs = 8_000
    b = design_lowpass(129, 1_000, fs, window="hamming")
    inband = sine(200.0, amplitude=1.0, duration=1.0, sampling_rate=fs)
    stopband = sine(3_000.0, amplitude=1.0, duration=1.0, sampling_rate=fs)
    y_in = fir_filter(inband, b, zero_phase=True).samples
    y_stop = fir_filter(stopband, b, zero_phase=True).samples
    rms_in = float(np.sqrt(np.mean(y_in**2)))
    rms_stop = float(np.sqrt(np.mean(y_stop**2)))
    assert rms_in > 0.6                 # passband preserved
    assert rms_stop < 0.1 * rms_in      # >= 20 dB suppression


def test_highpass_attenuates_low_frequencies():
    fs = 8_000
    b = design_highpass(129, 1_000, fs, window="hamming")
    low = sine(100.0, amplitude=1.0, duration=1.0, sampling_rate=fs)
    high = sine(3_000.0, amplitude=1.0, duration=1.0, sampling_rate=fs)
    y_low = fir_filter(low, b, zero_phase=True).samples
    y_high = fir_filter(high, b, zero_phase=True).samples
    assert np.sqrt(np.mean(y_high**2)) > 0.6
    assert np.sqrt(np.mean(y_low**2)) < 0.1 * np.sqrt(np.mean(y_high**2))


def test_fir_filter_output_shape_and_fs(sine_440):
    b = design_lowpass(65, 1_000, 8_000, window="hamming")
    out = fir_filter(sine_440, b, zero_phase=True)
    assert out.n_samples == sine_440.n_samples
    assert out.sampling_rate == sine_440.sampling_rate
    assert np.all(np.isfinite(out.samples))


def test_butterworth_design_and_apply(noisy_tone):
    b, a = design_butterworth("lowpass", 100.0, 2_000.0, order=4)
    assert len(b) == 5 and len(a) == 5
    out = iir_filter(noisy_tone, b, a, zero_phase=True)
    assert out.n_samples == noisy_tone.n_samples
    assert np.all(np.isfinite(out.samples))
    # Noise above 100 Hz should be reduced: output energy < input energy.
    assert np.sum(out.samples**2) < np.sum(noisy_tone.samples**2)
