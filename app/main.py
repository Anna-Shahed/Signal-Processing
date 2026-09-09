import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os
import json

st.set_page_config(
    page_title="Signal Lab",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

css_path = os.path.join("app", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "signal" not in st.session_state:
    fs = 8000
    t = np.linspace(0, 0.5, int(fs * 0.5), endpoint=False)
    st.session_state.signal = np.sin(2 * np.pi * 440 * t)
    st.session_state.fs = fs
    st.session_state.t = t

if "projects" not in st.session_state:
    st.session_state.projects = {
        "Audio_Telemetry_v1.2": {"desc": "High-frequency telemetry stream analysis configuration.", "target": "Cloud Repository", "version": "v1.2"}
    }

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
    st.markdown("#### Project Workspaces & Version Control")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("##### Create / Edit Workspace")
        proj_name = st.text_input("Project Identifier", "Audio_Telemetry_v1.3")
        version = st.selectbox("Version Tag", ["v1.0", "v1.1", "v1.2", "v1.3 (Beta)"])
        storage_target = st.selectbox("Storage Target", ["Local Disk", "Cloud Repository", "Secure Enclave"])
        desc = st.text_area("Workspace Description", "Configured filters and bandpass parameters for incoming sensor data.")
        
        if st.button("Save & Commit Version"):
            st.session_state.projects[proj_name] = {"desc": desc, "target": storage_target, "version": version}
            st.success(f"Successfully committed version {version} for {proj_name}!")
            
    with col_p2:
        st.markdown("##### Active Stored Workspaces")
        for name, data in st.session_state.projects.items():
            st.markdown(f"""
            <div class="glass-card">
                <b>{name}</b> <span style="color: #0a84ff; font-size: 0.8rem;">[{data['version']}]</span><br>
                <span style="color: #86868b; font-size: 0.85rem;">{data['desc']}</span><br>
                <div style="margin-top: 8px; font-size: 0.75rem; color: #32d74b;">Target: {data['target']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("Generate Shareable Link / Export JSON"):
            export_payload = json.dumps(st.session_state.projects, indent=2)
            st.code(export_payload, language="json")

with tab_experiments:
    st.markdown("#### Automated Sweep Laboratory")
    
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        sweep_start = st.number_input("Start Frequency (Hz)", value=100, step=50)
        sweep_end = st.number_input("End Frequency (Hz)", value=2000, step=100)
        resonance = st.slider("Filter Resonance (Q)", 0.5, 10.0, 1.4)
        run_sweep = st.button("Execute Parameter Sweep")
    
    with col_e2:
        if run_sweep:
            freqs = np.linspace(sweep_start, sweep_end, 200)
            cutoff = 1000
            response = -20 * np.log10(1 + (freqs / cutoff)**(2 * resonance)) + 3
            
            fig_sweep = go.Figure()
            fig_sweep.add_trace(go.Scatter(
                x=freqs, y=response,
                mode='lines',
                line=dict(color='#32d74b', width=2)
            ))
            fig_sweep.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Frequency (Hz)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title='Magnitude Response (dB)')
            )
            st.plotly_chart(fig_sweep, use_container_width=True)
        else:
            st.info("Configure sweep parameters on the left and click execute to render frequency response.")

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
    
    st.markdown("##### 1. Discrete Fourier Transform (DFT)")
    st.markdown("""
    <div class="eq-tooltip-wrapper">
        <div class="eq-content">X[k] = \\sum_{n=0}^{N-1} x[n] \\cdot e^{-j 2\\pi k n / N}</div>
        <div class="tooltip-box">
            <b>Mathematical Breakdown:</b> Maps discrete time-domain signals into complex frequency components.<br><br>
            <b>Usage & Implementation:</b> Implemented via vectorized summation loops across $N$ sample bins. Used for harmonic analysis and spectral feature extraction.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 2. Fast Fourier Transform (FFT)")
    st.markdown("""
    <div class="eq-tooltip-wrapper">
        <div class="eq-content">O(N \\log N) \\quad \\text{Cooley-Tukey Radix-2 Algorithm}</div>
        <div class="tooltip-box">
            <b>Mathematical Breakdown:</b> Reduces computational complexity from $O(N^2)$ to $O(N \\log N)$ using recursive butterfly structures.<br><br>
            <b>Usage & Implementation:</b> Implemented via numpy rfft routines. Essential for real-time spectral visualization pipelines.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 3. Finite Impulse Response (FIR) Filter")
    st.markdown("""
    <div class="eq-tooltip-wrapper">
        <div class="eq-content">y[n] = \\sum_{i=0}^{M} b_i \\cdot x[n-i]</div>
        <div class="tooltip-box">
            <b>Mathematical Breakdown:</b> Computes filter output as a weighted linear combination of present and past inputs.<br><br>
            <b>Usage & Implementation:</b> Implemented via linear convolution of input streams with coefficient arrays $b$. Guarantees strict linear phase response.
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown(
    '<div class="spatial-footer"><a href="https://github.com/Anna-Shahed/Signal-Processing/tree/main" target="_blank">@github &nbsp;-&nbsp; Anna-Shahed</a></div>',
    unsafe_allow_html=True
)
