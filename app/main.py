import streamlit as st
from signal_processing.visualization.theme import apply_editorial_theme

st.set_page_config(page_title="Signal Lab", layout="wide", initial_sidebar_state="collapsed")

with open("app/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 1. Top Navigation
nav_cols = st.columns(6)
with nav_cols[0]: st.markdown("**Signal Lab**")
with nav_cols[1]: st.markdown("Projects")
# ... (Pipeline state tracker: INPUT → PROCESS → ANALYZE → RESULT)
st.markdown("<hr>", unsafe_allow_html=True)

# 2. Main Layout
left_rail, center_workspace, right_rail = st.columns([1.5, 5, 1.5], gap="large")

with left_rail:
    st.markdown("### SOURCE")
    # minimal selectboxes and sliders
    fs = st.number_input("Sampling Rate", 8000)
    dur = st.slider("Duration", 0.1, 5.0, 1.0)

with center_workspace:
    st.markdown("### TIME DOMAIN")
    # Render Plotly waveform (line_width=1, color="white")
    st.markdown("### FREQUENCY DOMAIN")

with right_rail:
    st.markdown("### ANALYSIS")
    st.metric("Dominant Freq", "440.0 Hz")
    st.metric("RMS", "0.707 V")
    st.metric("SNR", "12.4 dB")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### EVENTS")
