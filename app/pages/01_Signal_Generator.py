"""Signal Generator — synthesize deterministic test signals."""

from __future__ import annotations

import numpy as np
import streamlit as st

from components.charts import waveform_chart
from components.controls import export_buttons
from components.metrics import metric_card, status_led
from signal_processing.generators import (
    chirp,
    composite,
    cosine,
    gaussian_noise,
    sawtooth,
    sine,
    square,
    triangle,
    white_noise,
)

st.set_page_config(page_title="Signal Generator", page_icon="◈", layout="wide")
st.title("Signal Generator")
st.caption("Synthesize deterministic test signals for the laboratory.")

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Primary component")
    waveform = st.selectbox(
        "Waveform",
        ["sine", "cosine", "square", "triangle", "sawtooth", "chirp",
         "white noise", "gaussian noise"],
        key="gen_wave",
    )
    freq = st.slider("Frequency (Hz)", 1.0, 2_000.0, 220.0, 1.0, key="gen_freq")
    amp = st.slider("Amplitude", 0.01, 2.0, 1.0, 0.01, key="gen_amp")
    duration = st.slider("Duration (s)", 0.05, 5.0, 1.0, 0.05, key="gen_dur")
    sr = st.select_slider("Sampling rate (Hz)",
                          options=[1_000, 2_000, 4_000, 8_000, 16_000, 44_100],
                          value=8_000, key="gen_sr")
    if waveform == "chirp":
        f1 = st.slider("End frequency (Hz)", 1.0, min(8_000.0, sr / 2), 2_000.0,
                       key="gen_f1")
        kind = st.selectbox("Chirp law", ["linear", "logarithmic", "quadratic"],
                            key="gen_kind")
    if waveform in {"square", "sawtooth", "triangle"}:
        st.caption("Note: naive periodic waves alias near Nyquist — keep the "
                   "fundamental below fs/4 for clean spectra.")

    st.subheader("Noise")
    add_noise = st.checkbox("Add white noise", value=False, key="gen_noise")
    noise_amp = st.slider("Noise amplitude", 0.0, 1.0, 0.05, 0.01, key="gen_noise_amp")
    seed = st.number_input("Random seed", 0, 2**31 - 1, 42, key="gen_seed")
    generate = st.button("Generate signal", type="primary", key="gen_button")

if generate:
    if waveform == "sine":
        sig = sine(freq, amp, 0.0, duration, sr)
    elif waveform == "cosine":
        sig = cosine(freq, amp, 0.0, duration, sr)
    elif waveform == "square":
        sig = square(freq, amp, duration, sr)
    elif waveform == "triangle":
        sig = triangle(freq, amp, duration, sr)
    elif waveform == "sawtooth":
        sig = sawtooth(freq, amp, duration, sr)
    elif waveform == "chirp":
        sig = chirp(freq, f1, duration, sr, kind=kind, amplitude=amp)
    elif waveform == "white noise":
        sig = white_noise(duration, sr, amplitude=amp, seed=seed)
    else:
        sig = gaussian_noise(duration, sr, amplitude=amp, seed=seed)

    if add_noise:
        sig = composite(sig, white_noise(duration, sr, amplitude=noise_amp, seed=seed))

    st.session_state["sig"] = sig
    st.session_state["sig_name"] = waveform if not add_noise else f"{waveform} + noise"

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

with right:
    st.subheader("Waveform")
    st.plotly_chart(waveform_chart(sig, height=380), use_container_width=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Samples", f"{sig.n_samples:,}")
    with c2:
        metric_card("Duration", f"{sig.duration:.3f}", unit="s")
    with c3:
        metric_card("Sampling rate", f"{sig.sampling_rate:g}", unit="Hz")
    with c4:
        metric_card("Peak", f"{float(np.max(np.abs(sig.samples))):.4f}")
    st.divider()
    export_buttons(sig, key="gen_export")
    status_led(f"Active signal: {st.session_state.get('sig_name', 'sine')} — "
               f"shared with all other pages", ok=True)
