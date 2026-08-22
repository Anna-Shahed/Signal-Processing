from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import streamlit as st

from app import components as ui
from signal_processing.analysis import analyze
from signal_processing.generators import composite, sine, white_noise

RESULTS_DIR = Path("benchmarks/results")
SWEEP_PARAMS = ["frequency", "noise_amplitude", "duration"]

def _run_one(frequency: float, noise: float, fs: float,
             duration: float, seed: int) -> dict:
    tone = sine(frequency, amplitude=1.0, duration=duration, sampling_rate=fs)
    signal = (composite(tone, white_noise(duration, fs, amplitude=noise, seed=seed))
              if noise > 0 else tone)
    m = analyze(signal).metrics
    return {
        "frequency": frequency,
        "noise": noise,
        "duration": duration,
        "dominant_frequency": m.get("dominant_frequency", float("nan")),
        "snr_db": m.get("snr_db", float("nan")),
        "rms": m.get("rms", float("nan")),
        "crest_factor": m.get("crest_factor", float("nan")),
    }

def _table_html(rows: list[dict], columns: list[str]) -> str:
    head = "".join(f"<th>{c.replace('_', ' ')}</th>" for c in columns)
    body = ""
    for r in rows:
        cells = "".join(
            f"<td>{r[c]:.4g}</td>" if isinstance(r[c], float) else f"<td>{r[c]}</td>"
            for c in columns
        )
        body += f"<tr>{cells}</tr>"
    return (
        "<style>"
        ".sp-table{border-collapse:collapse;width:100%;font-family:var(--mono);"
        "font-size:11px;color:var(--ink-2);}"
        ".sp-table th{font-size:9px;letter-spacing:0.18em;text-transform:uppercase;"
        "color:var(--ink-3);text-align:left;padding:0.5rem 0.75rem;font-weight:400;"
        "border-bottom:1px solid var(--hairline-strong);}"
        ".sp-table td{padding:0.5rem 0.75rem;border-bottom:1px solid var(--hairline);}"
        "</style>"
        f'<table class="sp-table"><thead><tr>{head}</tr></thead>'
        f"<tbody>{body}</tbody></table>"
    )


def render() -> None:
    ui.section_header("Parameters")
    c1, c2, c3 = st.columns(3)
    with c1:
        sweep = st.selectbox("Sweep", SWEEP_PARAMS)
    with c2:
        fs = st.number_input("Sampling rate (Hz)", 1_000, 96_000, 8_000, step=1_000)
    with c3:
        seed = st.number_input("Seed", 0, 10_000, 42, step=1)

    if sweep == "frequency":
        start, stop = st.slider("Frequency range (Hz)", 50.0, 5_000.0, (100.0, 1_000.0))
    elif sweep == "noise_amplitude":
        start, stop = st.slider("Noise amplitude", 0.0, 1.0, (0.0, 0.5))
    else:
        start, stop = st.slider("Duration range (s)", 0.1, 5.0, (0.5, 2.0))
    steps = st.slider("Steps", 3, 50, 10)

    if st.button("Run sweep", type="primary"):
        rows = []
        for value in np.linspace(start, stop, steps):
            kwargs = {"noise": 0.05, "duration": 1.0,
                      "fs": float(fs), "seed": int(seed)}
            if sweep == "frequency":
                kwargs["frequency"] = float(value)
            elif sweep == "noise_amplitude":
                kwargs["frequency"], kwargs["noise"] = 440.0, float(value)
            else:
                kwargs["frequency"], kwargs["duration"] = 440.0, float(value)
            rows.append(_run_one(**kwargs))

        ui.section_header(f"Sweep · {sweep}")
        st.markdown(_table_html(rows, list(rows[0])), unsafe_allow_html=True)

        valid = [r for r in rows if r["snr_db"] == r["snr_db"]]
        best = max(valid, key=lambda r: r["snr_db"]) if valid else rows[0]
        ui.section_header("Summary")
        ui.readout("Best SNR", f"{best['snr_db']:.1f}", "dB")
        ui.readout("At frequency", f"{best['frequency']:.1f}", "Hz")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = RESULTS_DIR / f"experiment_{sweep}_{stamp}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        ui.metadata_row(f"exported -> {out}")
