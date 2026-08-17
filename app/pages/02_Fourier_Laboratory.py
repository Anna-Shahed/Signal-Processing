"""Fourier Laboratory — spectrum inspection with amplitude-corrected windows."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from scipy.signal import find_peaks

from components.charts import phase_chart, spectrum_chart
from components.metrics import metric_card, status_led
from signal_processing.analysis.spectral import magnitude_spectrum
from signal_processing.generators import sine
from signal_processing.transforms.dft import dft
from signal_processing.transforms.fft import fft_radix2_educational

st.set_page_config(page_title="Fourier Laboratory", page_icon="◈", layout="wide")
st.title("Fourier Laboratory")
st.caption("Discrete Fourier analysis with educational and production backends.")

sig = st.session_state.get("sig")
if sig is None:
    sig = sine(220.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
    st.session_state["sig"] = sig
    st.session_state["sig_name"] = "sine"

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Analysis settings")
    window = st.selectbox("Window", [None, "hann", "hamming", "blackman", "kaiser"],
                          format_func=lambda w: "none (rectangular)" if w is None else w,
                          key="fft_win")
    pad = st.selectbox("Zero padding", ["none", "next power of two", "2× length", "4× length"],
                       key="fft_pad")
    db = st.checkbox("Show dB (20·log10|X|)", value=True, key="fft_db")
    peaks_n = st.slider("Top peaks", 1, 20, 5, key="fft_peaks")

    st.subheader("Educational check")
    st.caption("Direct DFT is O(N²); the radix-2 FFT is O(N log N). "
               "Both are compared on the first 128 samples below.")
    st.code("dft(x)  vs  fft_radix2(x)", language="text")

n = len(sig.samples)
if pad == "none":
    n_fft = n
elif pad == "next power of two":
    n_fft = int(2 ** np.ceil(np.log2(n)))
elif pad == "2× length":
    n_fft = 2 * n
else:
    n_fft = 4 * n

spec = magnitude_spectrum(sig, n=n_fft, window=window)

with right:
    st.subheader("Magnitude spectrum")
    st.plotly_chart(spectrum_chart(spec, db=db, height=360), use_container_width=True)
    st.subheader("Phase spectrum")
    st.plotly_chart(phase_chart(spec, height=280), use_container_width=True)

freqs = np.asarray(spec.frequencies)
mag = np.abs(np.asarray(spec.values))
peaks, props = find_peaks(mag, height=mag.max() * 1e-4)
order = np.argsort(props["peak_heights"])[::-1][:peaks_n]
rows = []
for idx in order:
    rows.append({
        "Frequency (Hz)": round(float(freqs[peaks[idx]]), 3),
        "Magnitude": round(float(mag[peaks[idx]]), 6),
        "Magnitude (dB)": round(float(20.0 * np.log10(max(mag[peaks[idx]], 1e-12))), 3),
    })
st.subheader("Dominant peaks")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

x = np.asarray(sig.samples[:128], dtype=float)
dft_v = dft(x)
fft_v = fft_radix2_educational(x)
max_err = float(np.max(np.abs(dft_v - fft_v)))

c1, c2, c3 = st.columns(3)
with c1:
    metric_card("DFT vs FFT max error", f"{max_err:.2e}")
with c2:
    metric_card("Dominant frequency", f"{spec.dominant_frequency:.3f}", unit="Hz")
with c3:
    metric_card("Spectral centroid", f"{spec.spectral_centroid:.3f}", unit="Hz")
status_led(f"One-sided spectrum · {'windowed (' + str(window) + ')' if window else 'rectangular'} "
           f"· coherent-gain corrected", ok=True)
