from __future__ import annotations

import streamlit as st

from app import components as ui

TOPICS = [
    (
        "The Discrete Fourier Transform",
        [
            (
                "X[k] = Σₙ x[n] · e^(−2πi·k·n/N)",
                "The DFT decomposes a signal into N complex sinusoids. Each bin k "
                "measures how much of frequency k·fs/N lives in the signal.",
            ),
            (
                "|X[k]| = √(Re² + Im²)",
                "The magnitude spectrum — the amplitude of each frequency component. "
                "Peaks here are the signal's dominant tones.",
            ),
        ],
    ),
    (
        "The Fast Fourier Transform",
        [
            (
                "FFT: O(N log N) — Cooley–Tukey",
                "The FFT reuses overlapping sub-problems, cutting the DFT's O(N²) "
                "work to O(N log N). This repo implements both, and proves they agree.",
            ),
        ],
    ),
    (
        "The Short-Time Fourier Transform",
        [
            (
                "STFT{m,k} = Σₙ x[m·H + n] · w[n] · e^(−2πi·k·n/W)",
                "A windowed DFT sliding across time (hop H). The spectrogram is "
                "|STFT|² — time on one axis, frequency on the other.",
            ),
        ],
    ),
    (
        "The Discrete Wavelet Transform",
        [
            (
                "cA, cD = DWT(x) — low-pass + high-pass splits",
                "The DWT splits the signal into approximation (cA) and detail (cD) "
                "coefficients, revealing structure at multiple scales at once.",
            ),
        ],
    ),
    (
        "Filtering",
        [
            (
                "y[n] = Σₖ b[k] · x[n−k]",
                "A finite-impulse-response (FIR) filter: each output is a weighted "
                "sum of the last K inputs. The weights b are the filter's impulse response.",
            ),
        ],
    ),
]


def render() -> None:
    ui.section_header("Mathematics")
    st.markdown(
        "<style>"
        ".sp-eq{font-family:'Apple Garamond','EB Garamond','Garamond',Georgia,serif;"
        "font-style:italic;font-weight:700;font-size:16px;color:#d6d6dc;"
        "border-bottom:1px dashed rgba(255,255,255,0.18);cursor:help;padding:0.15rem 0.1rem;}"
        ".sp-eq:hover{color:#ffffff;}"
        ".sp-blurb{color:#9a9aa3;font-size:13.5px;line-height:1.55;margin:0.2rem 0 1rem;}"
        "</style>",
        unsafe_allow_html=True,
    )
    for title, entries in TOPICS:
        st.markdown(f"**{title}**")
        for eq, blurb in entries:
            st.markdown(
                f'<div class="sp-eq" title="{blurb}">{eq}</div>'
                f'<div class="sp-blurb">{blurb}</div>',
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div class="sp-blurb">Hover any equation for the plain-English explanation.</div>',
        unsafe_allow_html=True,
    )
