"""File I/O: CSV, WAV, and JSON round-trips preserve data and metadata."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from signal_processing.generators import sine
from signal_processing.io import read_csv, read_wav, write_csv, write_json
from signal_processing.io.json import read_json, signal_from_json, to_json_string


def test_csv_time_value_roundtrip(tmp_path):
    sig = sine(100.0, amplitude=1.0, duration=0.5, sampling_rate=4_000)
    path = write_csv(sig, tmp_path / "sig.csv")
    back = read_csv(path)
    assert back.sampling_rate == pytest.approx(4_000)
    assert back.n_samples == sig.n_samples
    assert np.allclose(back.samples, sig.samples)


def test_csv_samples_only_requires_fs(tmp_path):
    path = tmp_path / "samples.csv"
    pd.DataFrame({"value": [1.0, 2.0, 3.0]}).to_csv(path, index=False)
    sig = read_csv(path, sampling_rate=500)
    assert sig.n_samples == 3
    assert sig.sampling_rate == 500


def test_wav_roundtrip(tmp_path):
    sig = sine(440.0, amplitude=0.5, duration=0.25, sampling_rate=8_000)
    path = write_wav(sig, tmp_path / "tone.wav")
    back = read_wav(path)
    assert back.sampling_rate == 8_000
    assert back.n_samples == 2_000
    assert np.allclose(back.samples, sig.samples, atol=1e-3)  # PCM_16 quantized


def test_signal_json_roundtrip(tmp_path):
    sig = sine(100.0, amplitude=1.0, duration=0.2, sampling_rate=1_000,
               name="tone", units="V", )
    path = write_json(sig, tmp_path / "sig.json")
    back = signal_from_json(path)
    assert np.allclose(back.samples, sig.samples)
    assert back.sampling_rate == 1_000
    assert back.name == "tone"
    assert back.units == "V"


def test_analysis_result_json_roundtrip(tmp_path, sine_440):
    from signal_processing.analysis import analyze
    result = analyze(sine_440)
    path = write_json(result, tmp_path / "analysis.json")
    payload = read_json(path)
    assert "metrics" in payload
    assert "dominant_frequency" in payload["metrics"]


def test_to_json_string_encodes_arrays():
    sig = sine(50.0, amplitude=1.0, duration=0.1, sampling_rate=1_000)
    text = to_json_string(sig)
    assert '"__ndarray__"' in text
    import json
    assert json.loads(text)["sampling_rate"] == 1_000
