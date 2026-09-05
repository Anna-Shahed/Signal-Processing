from __future__ import annotations

import io

import numpy as np
import streamlit as st

from app import components as ui
from app.engine import run_task
from app.state import get, reset_signal, set as set_state
from signal_processing.analysis import analyze
from signal_processing.analysis.anomaly import detect_anomalies
from signal_processing.analysis.events import detect_events
from signal_processing.filters import design_lowpass, fir_filter
from signal_processing.generators import chirp, composite, sine, square, white_noise
from signal_processing.io import read_csv, read_wav
from signal_processing.transforms.fft import fft
from signal_processing.visualization.plotly_template import (
    add_event_markers, editorial_figure, trace_spectrum, trace_waveform,
)

WAVEFORMS = ["sine", "square", "chirp", "sine + noise"]


def _generate(kind: str, fs: float, duration: float) -> None:
    try:
        if kind == "sine":
            sig = sine(440.0, amplitude=1.0, duration=duration, sampling_rate=fs)
        elif kind == "square":
            sig = square(110.0, amplitude=1.0, duration=duration, sampling_rate=fs)
        elif kind == "chirp":
            sig = chirp(100.0, 2_000.0, duration=duration, sampling_rate=fs, kind="linear")
        else:
            sig = composite(
                sine(440.0, amplitude=1.0, duration=duration, sampling_rate=fs),
                white_noise(duration, fs, amplitude=0.05, seed=42),
            )
        set_state("signal", sig)
        set_state("sample_rate", float(fs))
        reset_signal()
        set_state("signal", sig)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Generation failed: {exc}")


def _load_upload(uploaded) -> None:
    try:
        suffix = uploaded.name.rsplit(".", 1)[-1].lower()
        if suffix == "wav":
            sig = read_wav(io.BytesIO(uploaded.getvalue()))
        else:
            sig = read_csv(io.StringIO(uploaded.getvalue().decode("utf-8", errors="replace")))
        set_state("signal", sig)
        reset_signal()
        set_state("signal", sig)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load {uploaded.name}: {exc}")


def _run_pipeline() -> None:
    sig = get("signal")
    if sig is None:
        st.info("Generate or upload a signal first.")
        return

    def _work():
        stages: list[str] = []
        if st.session_state.get("stage_fft"):
            set_state("spectrum", fft(sig, one_sided=True))
            stages.append("FFT")
        processed = sig
        if st.session_state.get("stage_lowpass"):
            b = design_lowpass(64, 1_000, sig.sampling_rate, window="hamming")
            processed = fir_filter(sig, b, zero_phase=True)
            stages.append("LOWPASS 1 kHz")
        set_state("signal", processed)
        set_state("pipeline_steps", stages)
        result = analyze(processed)
        set_state("analysis", result)
        set_state("events", detect_events(processed, method="adaptive", threshold=0.4))
        set_state("anomalies", detect_anomalies(processed, method="zscore"))
        return result

    run_task("Running pipeline", _work)


def render() -> None:
    ui.pipeline_bar(get("pipeline_steps") or None)

    left, center, right = st.columns([260, 1, 300], gap="medium")

    with left:
        st.markdown('<div class="sp-rail">', unsafe_allow_html=True)
        ui.section_header("Source")
        uploaded = st.file_uploader("Import signal", type=["wav", "csv", "json"],
                                    label_visibility="collapsed")
        if uploaded is not None:
            _load_upload(uploaded)
        kind = st.selectbox("Signal type", WAVEFORMS, label_visibility="collapsed")
        fs = st.number_input("Sampling rate (Hz)", 1_000, 96_000, 8_000, step=1_000)
        dur = st.number_input("Duration (s)", 0.1, 10.0, 1.0, step=0.1)
        if st.button("Generate", type="primary", use_container_width=True):
            _generate(kind, float(fs), float(dur))
        ui.metadata_row(f"fs={int(fs)}  dur={dur:.2f}s")
        ui.section_header("Pipeline")
        st.checkbox("FFT", value=True, key="stage_fft")
        st.checkbox("Lowpass 1 kHz (FIR)", key="stage_lowpass")
        if st.button("Run", type="primary", use_container_width=True):
            _run_pipeline()
        st.markdown('</div>', unsafe_allow_html=True)

    with center:
        sig = get("signal")
        if sig is None:
            ui.section_header("Time Domain")
            st.caption("Generate or upload a signal to begin.")
            ui.section_header("Frequency Domain")
            return

        ui.section_header("Time Domain")
        t = np.arange(sig.n_samples) / sig.sampling_rate
        fig = editorial_figure(height=300)
        fig.add_trace(trace_waveform(t, sig.samples))
        add_event_markers(fig, [ev.start_time for ev in (get("events") or [])])
        fig.update_xaxes(title_text="time (s)")
        fig.update_yaxes(title_text=sig.units or "amplitude")
        st.plotly_chart(fig, use_container_width=True)
        ui.metadata_row(
            f"name={sig.name}  n={sig.n_samples}  "
            f"fs={int(sig.sampling_rate)}  t0=0  t1={sig.duration:.4f}s"
        )

        ui.section_header("Frequency Domain")
        spec = get("spectrum") or fft(sig, one_sided=True)
        if spec is not None:
            fig2 = editorial_figure(height=260)
            fig2.add_trace(trace_spectrum(spec.frequencies, np.abs(spec.values)))
            fig2.update_xaxes(title_text="frequency (Hz)")
            fig2.update_yaxes(title_text="magnitude")
            st.plotly_chart(fig2, use_container_width=True)
            df = float(spec.frequencies[1]) if spec.frequencies.size > 1 else 0.0
            ui.metadata_row(f"bins={spec.frequencies.size}  df={df:.2f}Hz")

    with right:
        st.markdown('<div class="sp-rail">', unsafe_allow_html=True)
        ui.section_header("Analysis")
        result = get("analysis")
        if result is None:
            st.caption("Run the pipeline to populate readouts.")
        else:
            m = result.metrics
            ui.readout("Dominant Frequency", f"{m.get('dominant_frequency', 0):.2f}", "Hz")
            ui.readout("RMS", f"{m.get('rms', 0):.4f}", sig.units or "")
            ui.readout("Peak Amplitude", f"{m.get('peak', 0):.4f}", sig.units or "")
            snr = m.get("snr_db", float("nan"))
            ui.readout("SNR", f"{snr:.1f}", "dB", alert=snr < 10)
        ui.section_header("Detected Events")
        events = get("events") or []
        ui.readout("Count", f"{len(events)}", alert=bool(events))
        for ev in events[:3]:
            ui.metadata_row(
                f"{ev.start_time:.3f}s -> {ev.end_time:.3f}s  conf={ev.confidence:.2f}"
            )
        ui.section_header("Anomalies")
        anomalies = get("anomalies") or []
        ui.readout("Count", f"{len(anomalies)}", alert=bool(anomalies))
        st.markdown('</div>', unsafe_allow_html=True)
