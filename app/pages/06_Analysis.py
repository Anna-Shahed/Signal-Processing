"""Signal Analysis — statistics, spectral features, and anomaly detection."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.metrics import metric_card, status_led
from signal_processing.analysis import analyze
from signal_processing.analysis.anomaly import detect_anomalies
from signal_processing.generators import sine
from signal_processing.io.json import to_json_string

st.set_page_config(page_title="Signal Analysis", page_icon="◈", layout="wide")
st.title("Signal Analysis")
st.caption("Statistical and spectral characterization of the active signal.")

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

result = analyze(sig)
metrics = result.metrics

st.subheader("Time-domain & spectral metrics")
rows = [{"Metric": k, "Value": v} for k, v in sorted(metrics.items())]
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Dominant frequency",
                f"{metrics.get('dominant_frequency', float('nan')):.3f}", unit="Hz")
with c2:
    metric_card("SNR", f"{metrics.get('snr_db', float('nan')):.2f}", unit="dB")
with c3:
    metric_card("RMS", f"{metrics.get('rms', float('nan')):.4f}")
with c4:
    metric_card("Peak-to-peak", f"{metrics.get('peak_to_peak', float('nan')):.4f}")

st.subheader("Anomaly detection")
method = st.selectbox("Method", ["zscore", "rolling", "robust", "amplitude", "energy"],
                      key="an_method")
threshold = st.slider("Threshold (σ)", 1.0, 8.0, 3.0, 0.1, key="an_thr")
anomalies = detect_anomalies(sig, method=method, threshold=threshold)
st.markdown(f"**{len(anomalies)} anomaly interval(s) detected**")
if anomalies:
    arows = [{
        "Start (s)": round(float(a.start_time), 4),
        "End (s)": round(float(a.end_time), 4),
        "Confidence": round(float(a.confidence), 3),
    } for a in anomalies]
    st.dataframe(pd.DataFrame(arows), use_container_width=True, hide_index=True)
else:
    st.info("No anomalies above the threshold.")

st.subheader("Export")
st.download_button("Download analysis (JSON)", to_json_string(result),
                   file_name="analysis.json", mime="application/json",
                   key="an_export", use_container_width=True)
status_led(f"Analysis of '{st.session_state.get('sig_name', 'sine')}'", ok=True)
