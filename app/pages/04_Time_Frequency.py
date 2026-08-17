"""Time-Frequency — STFT spectrogram laboratory."""

from __future__ import annotations

import streamlit as st

from components.charts import spectrogram_chart
from components.metrics import metric_card, status_led
from signal_processing.generators import sine
from signal_processing.transforms.stft import stft

st.set_page_config(page_title="Time-Frequency Analysis", page_icon="◈", layout="wide")
st.title("Time-Frequency Analysis")
st.caption("Short-Time Fourier Transform with COLA-compliant window defaults.")

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("STFT settings")
    window = st.selectbox("Window", ["hann", "hamming", "blackman", "kaiser"],
                          key="tf_win")
    nperseg = st.select_slider("Window length (samples)",
                               options=[64, 128, 256, 512, 1024],
                               value=256, key="tf_nperseg")
    hop = st.select_slider("Hop length (samples)",
                           options=[32, 64, 128, 256, 512],
                           value=128, key="tf_hop")
    db = st.checkbox("dB scale (20·log10|STFT|)", value=True, key="tf_db")
    vmin_db = st.slider("Floor (dB)", -120, -30, -80, key="tf_vmin")

with right:
    st.subheader("Spectrogram")
    if hop > nperseg:
        st.warning("Hop length exceeds window length — gaps appear between frames.")
    spec = stft(sig, nperseg=nperseg, hop_length=hop, window=window)
    st.plotly_chart(spectrogram_chart(spec, db=db, height=460, vmin_db=vmin_db),
                    use_container_width=True)
    df = float(spec.frequencies[1] - spec.frequencies[0])
    dt = float(spec.times[1] - spec.times[0])
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Frames", f"{spec.times.size:,}")
    with c2:
        metric_card("Frequency bins", f"{spec.frequencies.size:,}")
    with c3:
        metric_card("Δf resolution", f"{df:.2f}", unit="Hz")
    with c4:
        metric_card("Δt resolution", f"{dt:.4f}", unit="s")
    cola = (window == "hann" and hop == nperseg // 2)
    status_led(f"COLA condition: {'satisfied (hann, 50% overlap)' if cola else 'verify overlap-add'}"
               f" · Nyquist {sig.sampling_rate / 2:g} Hz", ok=hop <= nperseg)
