import streamlit as st

if "signal_data" not in st.session_state:
    st.session_state.signal_data = None
if "sample_rate" not in st.session_state:
    st.session_state.sample_rate = 8000
if "pipeline_steps" not in st.session_state:
    st.session_state.pipeline_steps = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Signal Lab"

try:
    with open("app/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    '<div class="spatial-footer">@github &nbsp;-&nbsp; Anna-Shahed</div>',
    unsafe_allow_html=True
)
