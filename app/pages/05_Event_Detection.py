"""Event Detection — threshold, adaptive, and peak-based strategies."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from components.charts import waveform_chart
from components.metrics import metric_card, status_led
from signal_processing.analysis.events import detect_events
from signal_processing.generators import sine

st.set_page_config(page_title="Event Detection", page_icon="◈", layout="wide")
st.title("Event Detection")
st.caption("Detect transient events with threshold, adaptive, and peak strategies.")

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Detector")
    method = st.selectbox("Method", ["threshold", "adaptive", "peak"], key="ev_method")
    threshold = st.slider("Threshold (absolute)", 0.0, 2.0, 0.5, 0.01, key="ev_thr")
    if method == "adaptive":
        base = st.slider("Adaptive base (RMS multiplier)", 0.5, 6.0, 2.0, 0.1,
                         key="ev_base")
    if method == "peak":
        min_distance = st.slider("Minimum distance (samples)", 1, 512, 64, key="ev_mind")
        prominence = st.slider("Prominence", 0.0, 1.0, 0.1, 0.01, key="ev_prom")

# Live recompute: the detector behaves like an instrument that tracks its knobs.
if method == "threshold":
    events = detect_events(sig, method="threshold", threshold=threshold)
elif method == "adaptive":
    events = detect_events(sig, method="adaptive", rms_multiplier=base)
else:
    events = detect_events(sig, method="peak", min_distance=min_distance,
                           prominence=prominence)
st.session_state["ev_events"] = events

with right:
    st.subheader("Waveform with detected events")
    st.plotly_chart(waveform_chart(sig, events=events, height=380),
                    use_container_width=True)
    if events:
        rows = [{
            "Start (s)": round(float(e.start_time), 4),
            "End (s)": round(float(e.end_time), 4),
            "Peak (s)": round(float(e.peak_time), 4),
            "Amplitude": round(float(e.amplitude), 4),
            "Duration (s)": round(float(e.duration), 4),
            "Confidence": round(float(e.confidence), 3),
        } for e in events]
        st.subheader(f"Detected events ({len(rows)})")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Events", f"{len(events):,}")
        with c2:
            metric_card("Mean duration",
                        f"{float(np.mean([e.duration for e in events])):.4f}", unit="s")
        with c3:
            metric_card("Max amplitude",
                        f"{float(max(e.amplitude for e in events)):.4f}")
    else:
        st.info("No events detected with the current settings.")
    status_led("Events computed live from the active session signal", ok=True)
