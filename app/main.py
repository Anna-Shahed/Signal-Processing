import streamlit as st
import os

st.set_page_config(
    page_title="Signal Lab",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load pure black Apple CSS
css_path = os.path.join("app", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Initialization
if "signal" not in st.session_state:
    st.session_state.signal = None

st.markdown("### Signal Lab")

tab_lab, tab_projects, tab_experiments, tab_analysis, tab_docs = st.tabs([
    "Lab", "Projects", "Experiments", "Analysis", "Documentation"
])

with tab_lab:
    st.markdown("#### Generator Configuration")
    col1, col2 = st.columns([1, 2])
    with col1:
        signal_type = st.selectbox("Type", ["Sine", "Cosine", "Noise"])
        freq = st.slider("Frequency", 50, 2000, 440)
    with col2:
        st.markdown("#### Output Stream")
        st.info("Configure parameters to initialize signal processing pipeline.")

with tab_projects:
    st.markdown("#### Projects")

with tab_experiments:
    st.markdown("#### Experiments")

with tab_analysis:
    st.markdown("#### Analysis")

with tab_docs:
    st.markdown("#### Documentation")

# Persistent Global Footer
st.markdown(
    '<div class="spatial-footer"><a href="https://github.com/Anna-Shahed/Signal-Processing/tree/main" target="_blank">@github - Anna-Shahed</a></div>',
    unsafe_allow_html=True
)
