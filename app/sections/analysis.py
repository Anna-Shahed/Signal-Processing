
from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components as ui
from app.state import get
from signal_processing.analysis import analyze
from signal_processing.analysis.anomaly import detect_anomalies
from signal_processing.analysis.events import detect_events
from signal_processing.io import write_csv, write_json, write_wav

OUT = Path("exports")

def _fmt(value, spec: str = ".4f") -> str:
    try:
        return f"{value:{spec}}"
    except (TypeError, ValueError):
        return "—"

def render() -> None:
    signal = get("signal")
    if signal is None:
        st.caption("No signal loaded. Generate or open one from the Signal Lab.")
        return

    result = analyze(signal)
    m = result.metrics

    left, right = st.columns(2)
    with left:
        ui.section_header("Statistics")
        for key, spec in [
            ("mean", ".5f"), ("median", ".5f"), ("variance", ".5f"),
            ("std", ".5f"), ("rms", ".5f"), ("peak_to_peak", ".5f"),
            ("crest_factor", ".4f"), ("skewness", ".4f"), ("kurtosis", ".4f"),
            ("energy", ".4f"), ("snr_db", ".2f"),
        ]:
            ui.readout(key.replace("_", " ").title(),
                       _fmt(m.get(key, float("nan")), spec))
    with right:
        ui.section_header("Spectral")
        for key, spec in [
            ("dominant_frequency", ".2f"), ("spectral_centroid", ".2f"),
            ("spectral_bandwidth", ".2f"), ("spectral_rolloff", ".2f"),
            ("spectral_flatness", ".5f"), ("spectral_entropy", ".5f"),
            ("zero_crossing_rate", ".5f"),
        ]:
            ui.readout(key.replace("_", " ").title(),
                       _fmt(m.get(key, float("nan")), spec))

    ui.section_header("Detected Events")
    events = detect_events(signal, method="adaptive", threshold=0.4)
    ui.readout("Count", f"{len(events)}", alert=bool(events))
    for ev in events[:8]:
        ui.metadata_row(
            f"t={ev.start:.3f}s → {ev.end:.3f}s  dur={ev.duration:.3f}s  "
            f"conf={ev.confidence:.2f}"
        )

    ui.section_header("Anomalies")
    anomalies = detect_anomalies(signal, method="zscore")
    ui.readout("Count", f"{len(anomalies)}", alert=bool(anomalies))
    for an in anomalies[:8]:
        start = getattr(an, "start", 0.0)
        end = getattr(an, "end", start)
        ui.metadata_row(f"t={start:.3f}s → {end:.3f}s")

    ui.section_header("Export")
    OUT.mkdir(parents=True, exist_ok=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("WAV", use_container_width=True):
            write_wav(signal, OUT / "analysis.wav")
            ui.metadata_row("-> exports/analysis.wav")
    with c2:
        if st.button("CSV", use_container_width=True):
            write_csv(signal, OUT / "analysis.csv")
            ui.metadata_row("-> exports/analysis.csv")
    with c3:
        if st.button("JSON", use_container_width=True):
            write_json(result, OUT / "analysis.json")
            ui.metadata_row("-> exports/analysis.json")
