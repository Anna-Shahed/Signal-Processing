"""Documentation — the mathematics and API reference, set in editorial type.
Content mirrors docs/mathematics.md; keep both in sync."""

from __future__ import annotations

import streamlit as st

from app import components as ui

TOPICS: list[tuple[str, list[str]]] = [
    ("Sampling Theorem",
     ["A continuous signal must be sampled at fs ≥ 2·fmax (Nyquist rate) to be "
      "recoverable without error.",
      "```\nx[n] = xc(n·Ts),   Ts = 1/fs\n```"]),
    ("Aliasing",
     ["Frequency content above fs/2 folds back into the band 0..fs/2 and becomes "
      "indistinguishable from a legitimate component.",
      "```\nf_alias = |f - k·fs|,   k = round(f / fs)\n```"]),
    ("DFT",
     ["The direct (educational) DFT is O(N²).",
      "```\nX[k] = Σ_n x[n]·exp(-j·2π·kn/N)\n```"]),
    ("FFT",
     ["The radix-2 Cooley–Tukey FFT is O(N log N) and requires N = 2^m. The "
      "production path uses NumPy's FFT; both agree to ~1e-8 in tests.",
      "```\nX = fft(x);  x = ifft(X)\n```"]),
    ("Convolution Theorem",
     ["Multiplication in the frequency domain equals convolution in the time "
      "domain, enabling FFT convolution at O(N log N).",
      "```\nx ⊛ h = IFFT(FFT(x) · FFT(h))\n```"]),
    ("Windowing & Leakage",
     ["A finite observation window convolves the spectrum with the window's "
      "transform, smearing energy across bins. Hann/Hamming reduce sidelobes.",
      "```\ncoherent gain = mean(window)\n```"]),
    ("STFT",
     ["The spectrogram slices the signal into overlapping frames, windows each, "
      "and FFTs them — COLA-compliant Hann at 50% overlap enables exact ISTFT.",
      "```\nS[m, k] = FFT(x[m·hop : m·hop + n] · w)\n```"]),
    ("Filtering",
     ["FIR: windowed-sinc design, linear phase, cost O(M) per sample. IIR: "
      "Butterworth/Chebyshev, steep rolloff at low order, nonlinear phase.",
      "```\ny[n] = Σ_k b[k]·x[n-k]   (FIR)\n```"]),
    ("PSD",
     ["The periodogram is the squared magnitude of the DFT; Welch's method "
      "averages periodograms over overlapping, windowed segments to reduce "
      "variance.",
      "```\nP[k] = |X[k]|² / (fs · Σ w²)\n```"]),
    ("Kalman Filter",
     ["A linear-Gaussian recursive estimator: predict with the state model, "
      "then correct with the measurement model weighted by covariance.",
      "```\nx̂ₖ = F·x̂ₖ₋₁ ;  x̂ₖ = x̂ₖ + K·(zₖ - H·x̂ₖ)\n```"]),
]

API_TABLE = [
    ("signal_processing", "Signal, Spectrum, Spectrogram, Event, AnalysisResult"),
    ("generators", "sine, cosine, square, triangle, sawtooth, chirp, white_noise, composite"),
    ("transforms", "dft, idft, fft, ifft, fft_radix2_educational, stft, istft, dwt, idwt"),
    ("filters", "design_lowpass/highpass/bandpass/bandstop, fir_filter, "
                "design_butterworth, iir_filter, frequency_response"),
    ("operations", "convolve, convolve_fft, circular_convolve, cross_correlation, resample"),
    ("analysis", "analyze, magnitude_spectrum, psd, detect_peaks, detect_events, detect_anomalies"),
    ("estimation", "KalmanFilter, periodogram, welch"),
    ("pipelines", "Pipeline, detrend, normalize, lowpass, fft_stage"),
    ("io", "read_csv, write_csv, read_wav, write_wav, write_json"),
]

def render() -> None:
    ui.section_header("Mathematics")
    for title, lines in TOPICS:
        st.markdown(f"**{title}**")
        for line in lines:
            st.markdown(line)
        st.markdown("<hr style='border-top:1px solid var(--hairline);margin:.7rem 0'>",
                    unsafe_allow_html=True)

    ui.section_header("API Reference")
    rows = "".join(
        f"<tr><td style='font-family:var(--mono);color:var(--ink);padding:.3rem .6rem'>"
        f"{module}</td><td style='font-family:var(--mono);color:var(--ink-2);"
        f"padding:.3rem .6rem'>{members}</td></tr>"
        for module, members in API_TABLE
    )
    st.markdown(
        "<style>"
        ".sp-api{width:100%;border-collapse:collapse;font-size:11px;}"
        ".sp-api td{border-bottom:1px solid var(--hairline);}"
        "</style>"
        f"<table class='sp-api'>{rows}</table>",
        unsafe_allow_html=True,
    )
