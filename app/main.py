import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Signal Lab",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load pure black Apple CSS
css_path = os.path.join("app", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "signal" not in st.session_state:
    fs = 8000
    t = np.linspace(0, 0.5, int(fs * 0.5), endpoint=False)
    st.session_state.signal = np.sin(2 * np.pi * 440 * t)
    st.session_state.fs = fs
    st.session_state.t = t

st.markdown("### Signal Lab")

tab_lab, tab_projects, tab_experiments, tab_analysis, tab_docs = st.tabs([
    "Lab", "Projects", "Experiments", "Analysis", "Documentation"
])

with tab_lab:
    col_ctrl, col_view = st.columns([1, 2], gap="large")
    
    with col_ctrl:
        st.markdown("#### Generator Configuration")
        signal_type = st.selectbox("Waveform Type", ["Sine", "Cosine", "Square", "White Noise"])
        freq = st.slider("Frequency (Hz)", 50, 2000, 440)
        fs = st.number_input("Sampling Rate (Hz)", value=8000, step=1000)
        duration = st.slider("Duration (s)", 0.1, 2.0, 0.5)
        
        if st.button("Generate Stream"):
            t = np.linspace(0, duration, int(fs * duration), endpoint=False)
            if signal_type == "Sine":
                sig = np.sin(2 * np.pi * freq * t)
            elif signal_type == "Cosine":
                sig = np.cos(2 * np.pi * freq * t)
            elif signal_type == "Square":
                sig = np.sign(np.sin(2 * np.pi * freq * t))
            else:
                sig = np.random.normal(0, 1, len(t))
            
            st.session_state.signal = sig
            st.session_state.fs = fs
            st.session_state.t = t
            st.rerun()

    with col_view:
        st.markdown("#### Output Stream")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.t[:1000],
            y=st.session_state.signal[:1000],
            mode='lines',
            line=dict(color='#0a84ff', width=1.5)
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Time (s)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Amplitude')
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_projects:
    st.markdown("#### Project Workspaces")
    st.markdown("Active workspace configurations and parameter profiles.")
    st.text_input("Project Identifier", "Signal_Processor_v1.0")

with tab_experiments:
    st.markdown("#### Automated Sweeps")
    st.markdown("Configure batch processing matrices across frequency and amplitude bands.")
    st.select_slider("Sweep Range (Hz)", options=[100, 250, 500, 1000, 2000, 4000], value=(100, 1000))

with tab_analysis:
    st.markdown("#### Spectral Domain Analysis")
    sig = st.session_state.signal
    fs = st.session_state.fs
    fft_vals = np.fft.rfft(sig)
    fft_freqs = np.fft.rfftfreq(len(sig), 1/fs)
    
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Scatter(
        x=fft_freqs, y=np.abs(fft_vals),
        mode='lines',
        line=dict(color='#32d74b', width=1.5)
    ))
    fig_fft.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Frequency (Hz)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Magnitude')
    )
    st.plotly_chart(fig_fft, use_container_width=True)

with tab_docs:
    st.markdown("#### Documentation & Specifications")
    st.markdown("System architecture, discrete transform definitions, and filter specifications.")
    st.code("Discrete Fourier Transform: X[k] = sum_{n=0}^{N-1} x[n] * exp(-j * 2*pi*k*n / N)", language="python")

# Persistent Global Footer Link
st.markdown(
    '<div class="spatial-footer"><a href="https://github.com/Anna-Shahed/Signal-Processing/tree/main" target="_blank">@github &nbsp;-&nbsp; Anna-Shahed</a></div>',
    unsafe_allow_html=True
)
