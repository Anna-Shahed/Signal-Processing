"""Signal Processing Laboratory — Streamlit entry point.

Run with:
    streamlit run app/main.py
or:
    signal-process lab

Pages are auto-discovered from ``app/pages/``. The Midnight theme is
injected here and shared by every page.
"""

from __future__ import annotations

import streamlit as st

from signal_processing.generators import sine
from signal_processing.visualization.theme import MIDNIGHT

st.set_page_config(
    page_title="Signal Processing Laboratory",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp {{ background-color: {MIDNIGHT['background']}; }}
html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', sans-serif; color: {MIDNIGHT['text']}; }}

[data-testid="stSidebar"] {{
    background-color: {MIDNIGHT['panel']};
    border-right: 1px solid {MIDNIGHT['border']};
}}
[data-testid="stSidebar"] * {{ color: {MIDNIGHT['text']}; }}

h1, h2, h3 {{ color: {MIDNIGHT['text']}; letter-spacing: -0.01em; }}
h1 {{ font-size: 1.55rem; }}
h2 {{ font-size: 1.18rem; border-bottom: 1px solid {MIDNIGHT['border']}; padding-bottom: 0.3rem; }}
h3 {{ font-size: 1.0rem; }}

[data-testid="stMetric"] {{
    background-color: {MIDNIGHT['surface']};
    border: 1px solid {MIDNIGHT['border']};
    border-radius: 8px;
    padding: 0.7rem 1rem;
}}
[data-testid="stMetricLabel"] {{ color: {MIDNIGHT['muted']}; }}
[data-testid="stMetricValue"] {{ color: {MIDNIGHT['accent']}; font-family: 'JetBrains Mono', monospace; }}

.stButton > button, .stDownloadButton > button {{
    background-color: {MIDNIGHT['surface_alt']};
    color: {MIDNIGHT['text']};
    border: 1px solid {MIDNIGHT['border']};
    border-radius: 6px;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: {MIDNIGHT['accent']}; color: {MIDNIGHT['accent']};
}}
.stButton > button[kind="primary"] {{
    background-color: {MIDNIGHT['accent']};
    color: #07121a;
    border: none;
    font-weight: 600;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{ background-color: {MIDNIGHT['accent']}; }}
.stSelectbox > div > div {{ background-color: {MIDNIGHT['surface_alt']}; border-color: {MIDNIGHT['border']}; color: {MIDNIGHT['text']}; }}

[data-testid="stDataFrame"] {{
    background-color: {MIDNIGHT['surface']};
    border: 1px solid {MIDNIGHT['border']};
    border-radius: 8px;
}}

code, pre {{ font-family: 'JetBrains Mono', monospace; color: {MIDNIGHT['accent_violet']}; }}
.stRadio label {{ color: {MIDNIGHT['muted']}; }}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------- session
if "sig" not in st.session_state:
    st.session_state["sig"] = sine(440.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
if "sig_name" not in st.session_state:
    st.session_state["sig_name"] = "default tone (440 Hz)"

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### ◈ Signal Processing Laboratory")
    st.caption("Scientific instrumentation console")
    st.divider()
    sig = st.session_state["sig"]
    st.markdown("**Active signal**")
    st.markdown(f"`{st.session_state['sig_name']}`")
    st.markdown(
        f"- samples : `{sig.n_samples:,}`\n"
        f"- fs      : `{sig.sampling_rate:g} Hz`\n"
        f"- duration: `{sig.duration:.3f} s`\n"
        f"- peak    : `{float(abs(sig.samples).max()):.4g}`"
    )
    st.divider()
    if st.button("Reset to default signal", key="reset_sig"):
        st.session_state["sig"] = sine(440.0, amplitude=1.0, duration=1.0, sampling_rate=8_000)
        st.session_state["sig_name"] = "default tone (440 Hz)"
        st.rerun()
    st.caption("Use the pages below to generate, transform, and analyze signals.")
