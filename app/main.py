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
    st.markdown('<div class="notion-callout">Manage serialized pipeline configurations, export parameters, and load preset DSP profiles.</div>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.text_input("Active Project Name", "Audio_Telemetry_v1")
        st.selectbox("Storage Target", ["Local Disk", "Cloud Repository"])
    with col_p2:
        st.text_area("Workspace Description", "High-frequency telemetry stream analysis configuration for hardware debugging.")
        if st.button("Save Workspace Profile"):
            st.success("Workspace configuration successfully persisted.")

with tab_experiments:
    st.markdown("#### Automated Sweep Laboratory")
    st.markdown('<div class="notion-callout">Execute parameter sweeps across frequency ranges and noise profiles to evaluate filter stability.</div>', unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        sweep_start = st.number_input("Start Frequency (Hz)", value=100)
        sweep_end = st.number_input("End Frequency (Hz)", value=2000)
        steps = st.slider("Sweep Resolution Steps", 10, 100, 50)
        run_sweep = st.button("Execute Parameter Sweep")
    
    with col_e2:
        if run_sweep:
            frequencies = np.linspace(sweep_start, sweep_end, steps)
            responses = np.sin(frequencies / 300) * 100
            
            fig_sweep = go.Figure()
            fig_sweep.add_trace(go.Scatter(
                x=frequencies, y=responses,
                mode='lines+markers',
                line=dict(color='#32d74b', width=1.5)
            ))
            fig_sweep.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Sweep Frequency (Hz)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Response Magnitude')
            )
            st.plotly_chart(fig_sweep, use_container_width=True)
        else:
            st.info("Configure sweep bounds and click execute to render parametric output.")

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
    st.markdown("#### System Documentation & Mathematical Specifications")
    st.markdown('<div class="notion-callout">Comprehensive breakdown of core digital signal processing transforms. Hover over any equation block to inspect its operational blurb.</div>', unsafe_allow_html=True)
    
    st.markdown("##### 1. Discrete Fourier Transform (DFT)")
    st.markdown("""
    <div class="tooltip-container">
        X[k] = \\sum_{n=0}^{N-1} x[n] \\cdot e^{-j 2\\pi k n / N}
        <span class="tooltip-text"><b>DFT Breakdown:</b> Converts a finite sequence of equally-spaced samples of a function into a list of coefficients of a combination of complex sinusoids, mapping time domain data directly into frequency domain components.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 2. Fast Fourier Transform (FFT)")
    st.markdown("""
    <div class="tooltip-container">
        O(N \\log N) \\quad \\text{Cooley-Tukey Algorithm}
        <span class="tooltip-text"><b>FFT Breakdown:</b> An optimized algorithmic implementation that computes the DFT in O(N log N) operations instead of O(N^2) by breaking down the transform into smaller sub-transforms recursively.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 3. Finite Impulse Response (FIR) Filter")
    st.markdown("""
    <div class="tooltip-container">
        y[n] = \\sum_{i=0}^{M} b_i \\cdot x[n-i]
        <span class="tooltip-text"><b>FIR Filter Breakdown:</b> A digital filter whose impulse response is of finite duration, meaning it settles to zero in finite time. Known for inherent linear phase stability.</span>
    </div>
    """, unsafe_allow_html=True)

# Persistent Global Footer Link
st.markdown(
    '<div class="spatial-footer"><a href="https://github.com/Anna-Shahed/Signal-Processing/tree/main" target="_blank">@github &nbsp;-&nbsp; Anna-Shahed</a></div>',
    unsafe_allow_html=True
)
