"""Filter Designer — design and apply FIR / IIR filters with live preview."""

from __future__ import annotations

import numpy as np
import streamlit as st

from components.charts import compare_chart, filter_response_chart
from components.controls import export_buttons
from components.metrics import metric_card, status_led
from signal_processing.filters import (
    design_bandpass,
    design_bandstop,
    design_butterworth,
    design_highpass,
    design_lowpass,
    fir_filter,
    iir_filter,
)
from signal_processing.generators import sine

st.set_page_config(page_title="Filter Designer", page_icon="◈", layout="wide")
st.title("Filter Designer")
st.caption("Windowed-sinc FIR and Butterworth IIR design with live response preview.")

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Design")
    kind = st.radio("Filter family", ["FIR (windowed-sinc)", "IIR (Butterworth)"],
                    horizontal=True, key="fd_kind")
    ftype = st.selectbox("Type", ["lowpass", "highpass", "bandpass", "bandstop"],
                         key="fd_type")
    if kind.startswith("FIR"):
        order = st.slider("Number of taps", 8, 512, 101, step=1, key="fd_taps")
        window = st.selectbox("Window", ["hamming", "hann", "blackman", "kaiser"],
                              key="fd_win")
        zero_phase = st.checkbox("Zero-phase (filtfilt)", value=True, key="fd_zp")
    else:
        order = st.slider("Order", 1, 10, 4, key="fd_order")
        zero_phase = st.checkbox("Zero-phase (filtfilt)", value=True, key="fd_zp2")

    fs = sig.sampling_rate
    nyquist_guard = fs / 2.0 - 1.0
    if ftype in {"lowpass", "highpass"}:
        cutoff = st.slider("Cutoff (Hz)", 1.0, nyquist_guard,
                           float(min(500.0, nyquist_guard)), 1.0, key="fd_fc")
        cutoffs = cutoff
    else:
        lo = st.slider("Lower cutoff (Hz)", 1.0, nyquist_guard,
                       float(max(1.0, fs * 0.1)), 1.0, key="fd_fl")
        hi = st.slider("Upper cutoff (Hz)", lo + 1.0, nyquist_guard,
                       float(max(lo + 1.0, fs * 0.4)), 1.0, key="fd_fh")
        cutoffs = (lo, hi)

    st.button("Design & apply", type="primary", key="fd_apply")

a = [1.0]
if kind.startswith("FIR"):
    numtaps = order + 1 if order % 2 == 0 else order
    if ftype == "lowpass":
        b = design_lowpass(numtaps, cutoffs, fs, window=window)
    elif ftype == "highpass":
        b = design_highpass(numtaps, cutoffs, fs, window=window)
    elif ftype == "bandpass":
        b = design_bandpass(numtaps, cutoffs[0], cutoffs[1], fs, window=window)
    else:
        b = design_bandstop(numtaps, cutoffs[0], cutoffs[1], fs, window=window)
    filtered = fir_filter(sig, b, zero_phase=zero_phase)
    family_label = f"FIR · {numtaps} taps · {window}"
else:
    b, a = design_butterworth(ftype, cutoffs, fs, order=order)
    filtered = iir_filter(sig, b, a, zero_phase=zero_phase)
    family_label = f"Butterworth · order {order}"

with right:
    st.subheader("Frequency response")
    st.plotly_chart(filter_response_chart(b, a, fs=fs, height=460),
                    use_container_width=True)
    st.subheader("Original vs filtered")
    st.plotly_chart(compare_chart(sig, filtered, height=330),
                    use_container_width=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Filter", family_label)
    with c2:
        metric_card("Cutoff(s)", f"{cutoffs}", unit="Hz")
    with c3:
        metric_card("Peak (filtered)", f"{float(np.max(np.abs(filtered.samples))):.4f}")
    st.divider()
    export_buttons(filtered, key="fd_export")
    status_led(f"{ftype} · {'zero-phase' if zero_phase else 'causal'} · "
               f"cutoff(s) below Nyquist ({fs / 2:g} Hz)", ok=True)
