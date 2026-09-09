import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration & Spatial Theme Setup
st.set_page_config(
    page_title="Signal Lab | DSP Instrument",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Apple Vision Pro Spatial Styles & SF Font Stack
st.markdown("""
<style>
    :root {
      --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
      --bg-space: #07070a;
    }

    html, body, [class*="css"] {
      font-family: var(--font-sans) !important;
      background-color: var(--bg-space) !important;
      color: #f3f4f6 !important;
    }

    .stApp {
      background: radial-gradient(circle at 50% -20%, #16162c 0%, #07070a 70%) !important;
    }

    /* Glassmorphic Containers */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"], 
    div[data-testid="stExpander"], 
    div.stMetric,
    div[data-testid="stDataFrame"] {
      background: rgba(18, 18, 26, 0.65) !important;
      backdrop-filter: blur(24px) saturate(180%) !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      border-radius: 18px !important;
      padding: 1.25rem !important;
      box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4) !important;
    }

    /* Tactile Buttons */
    .stButton > button {
      background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.03)) !important;
      backdrop-filter: blur(12px) !important;
      border: 1px solid rgba(255, 255, 255, 0.18) !important;
      border-radius: 12px !important;
      color: #ffffff !important;
      font-family: var(--font-sans) !important;
      font-weight: 500 !important;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton > button:hover {
      background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.08)) !important;
      border-color: rgba(255, 255, 255, 0.4) !important;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0,0,0,0.5), 0 0 25px rgba(99, 102, 241, 0.25);
    }

    /* Fixed Global Spatial Footer Pill */
    .spatial-footer {
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(20, 20, 32, 0.85);
      backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 6px 18px;
      border-radius: 30px;
      font-family: var(--font-sans);
      font-size: 0.82rem;
      z-index: 999999;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    .spatial-footer a {
      color: rgba(255, 255, 255, 0.75);
      text-decoration: none;
      transition: color 0.2s ease;
    }

    .spatial-footer a:hover {
      color: #ffffff;
      text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 2. Robust Session State Initialization
if "signal" not in st.session_state:
    fs = 8000
    t = np.linspace(0, 1.0, fs, endpoint=False)
    st.session_state.signal = np.sin(2 * np.pi * 440 * t)
    st.session_state.fs = fs

# 3. App Header & Navigation Tabs
st.markdown("### **S I G N A L &nbsp; L A B** &nbsp; <span style='font-size: 0.8rem; color: #9ca3af;'>DSP INSTRUMENT</span>", unsafe_allow_html=True)

tab_lab, tab_projects, tab_experiments, tab_analysis, tab_docs = st.tabs([
    "Signal Lab", "Projects", "Experiments", "Analysis", "Documentation"
])

with tab_lab:
    st.markdown("#### Generator & Pipeline")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        signal_type = st.selectbox("Source Type", ["Sine Wave", "Cosine Wave", "White Noise", "Chirp"])
        freq = st.slider("Frequency (Hz)", 50, 2000, 440)
        fs = st.number_input("Sampling Rate (Hz)", value=8000, step=1000)
        duration = st.slider("Duration (s)", 0.1, 5.0, 1.0)
        
        if st.button("Generate Signal"):
            try:
                t = np.linspace(0, duration, int(fs * duration), endpoint=False)
                if signal_type == "Sine Wave":
                    sig = np.sin(2 * np.pi * freq * t)
                elif signal_type == "Cosine Wave":
                    sig = np.cos(2 * np.pi * freq * t)
                elif signal_type == "White Noise":
                    sig = np.random.normal(0, 1, len(t))
                else:
                    sig = np.chirp(t, f0=100, f1=freq, t1=duration)
                
                st.session_state.signal = sig
                st.session_state.fs = fs
                st.success("Signal generated successfully!")
            except Exception as e:
                st.error(f"Generation error: {e}")

    with col2:
        st.markdown("#### Time Domain Waveform")
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=st.session_state.signal[:1000], 
                mode='lines', 
                line=dict(color='#38bdf8', width=2)
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning("Generate or load a signal to visualize the waveform.")

with tab_projects:
    st.markdown("#### Saved Projects")
    st.info("Manage and persist your digital signal processing workflows here.")

with tab_experiments:
    st.markdown("#### Parameter Sweeps & Tests")
    st.info("Configure automated test matrices across frequency ranges and noise profiles.")

with tab_analysis:
    st.markdown("#### Spectral & FFT Analysis")
    try:
        sig = st.session_state.signal
        fs = st.session_state.fs
        fft_vals = np.fft.rfft(sig)
        fft_freqs = np.fft.rfftfreq(len(sig), 1/fs)
        
        fig_fft = go.Figure()
        fig_fft.add_trace(go.Scatter(
            x=fft_freqs, y=np.abs(fft_vals), 
            mode='lines', 
            line=dict(color='#a78bfa', width=2)
        ))
        fig_fft.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title='Frequency (Hz)', showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Magnitude', showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_fft, use_container_width=True)
    except Exception as e:
        st.warning("No spectral data available. Generate a signal in the Signal Lab tab.")

with tab_docs:
    st.markdown("#### Documentation & Mathematical Specifications")
    st.markdown("""
    - **Discrete Fourier Transform (DFT):** $X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j 2\pi k n / N}$
    - **Fast Fourier Transform (FFT):** $O(N \log N)$ Cooley-Tukey algorithm implementation.
    - **Digital Filtering:** FIR and IIR windowed filter design pipelines.
    """)

# 4. Persistent Global Footer Link
st.markdown(
    '<div class="spatial-footer"><a href="https://github.com/Anna-Shahed/Signal-Processing/tree/main" target="_blank">@github &nbsp;-&nbsp; Anna-Shahed</a></div>',
    unsafe_allow_html=True
)
