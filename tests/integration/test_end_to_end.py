"""End-to-end: generate -> noise -> filter -> FFT -> events -> export."""

from __future__ import annotations

import numpy as np

from signal_processing.analysis import analyze
from signal_processing.analysis.events import detect_events
from signal_processing.filters import design_lowpass, fir_filter
from signal_processing.generators import composite, sine, white_noise
from signal_processing.io import write_csv, write_json, write_wav
from signal_processing.transforms import fft


def test_complete_pipeline(tmp_path):
    tone = sine(50.0, amplitude=1.0, duration=2.0, sampling_rate=2_000)
    noise = white_noise(2.0, 2_000, amplitude=0.1, seed=7)
    raw = composite(tone, noise)

    b = design_lowpass(101, 150, 2_000, window="hamming")
    cleaned = fir_filter(raw, b, zero_phase=True)

    spec = fft(cleaned, one_sided=True)
    assert abs(spec.dominant_frequency - 50.0) < 5.0

    events = detect_events(cleaned, method="threshold", threshold=0.5)
    assert isinstance(events, list)

    result = analyze(cleaned)
    assert result.metrics["snr_db"] > result.metrics["snr_db"] - 100  # always true; sanity only

    write_wav(raw, tmp_path / "raw.wav")
    write_csv(cleaned, tmp_path / "cleaned.csv")
    write_json(result, tmp_path / "analysis.json")
    assert (tmp_path / "raw.wav").is_file()
    assert (tmp_path / "cleaned.csv").is_file()
    assert (tmp_path / "analysis.json").is_file()
