"""Event and anomaly detection on deterministic signals."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing import Signal
from signal_processing.analysis.anomaly import detect_anomalies
from signal_processing.analysis.events import detect_events
from signal_processing.generators import white_noise


def test_threshold_detects_two_bursts(burst_signal):
    events = detect_events(burst_signal, method="threshold", threshold=0.5)
    assert len(events) == 2
    for ev in events:
        assert ev.start_time < ev.peak_time < ev.end_time
        assert ev.duration > 0.0
        assert 0.0 <= ev.confidence <= 1.0
        assert ev.amplitude > 0.5


def test_event_durations_match_burst_widths(burst_signal):
    events = detect_events(burst_signal, method="threshold", threshold=0.5)
    durations = sorted(ev.duration for ev in events)
    # Each burst is 100 samples at 1 kHz -> ~0.1 s.
    assert all(abs(d - 0.1) < 0.05 for d in durations)


def test_adaptive_threshold_finds_bursts(noisy_tone):
    events = detect_events(noisy_tone, method="adaptive", rms_multiplier=3.0)
    assert isinstance(events, list)
    assert len(events) >= 1  # the tone itself is a sustained "event"


def test_peak_method_peak_times(burst_signal):
    events = detect_events(burst_signal, method="peak",
                           min_distance=50, prominence=0.5, min_height=0.5)
    peaks = sorted(ev.peak_time for ev in events)
    assert len(peaks) >= 2
    assert any(0.10 < p < 0.11 for p in peaks)   # first sine peak inside burst 1
    assert any(0.50 < p < 0.52 for p in peaks)   # first sine peak inside burst 2


def test_zscore_anomaly_finds_spike():
    fs = 1_000
    base = white_noise(1.0, fs, amplitude=0.01, seed=11).samples
    base[500] = 5.0
    sig = Signal(base, sampling_rate=fs)
    anomalies = detect_anomalies(sig, method="zscore", threshold=4.0)
    assert len(anomalies) >= 1
    assert any(a.start_time <= 0.5 <= a.end_time for a in anomalies)


def test_energy_anomaly_detects_high_energy_region():
    fs = 1_000
    x = np.zeros(fs)
    x[300:350] = 1.0
    sig = Signal(x, sampling_rate=fs)
    anomalies = detect_anomalies(sig, method="energy", threshold=4.0)
    assert any(a.start_time <= 0.35 <= a.end_time for a in anomalies)
