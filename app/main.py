from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components as ui
from app.state import init_state
from app.sections import analysis, docs, experiments, lab, projects

st.set_page_config(
    page_title="Signal Lab",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

css = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

init_state()

ui.render_top_nav()        

route = st.session_state.get("route", "lab")
if route == "projects":
    projects.render()
elif route == "experiments":
    experiments.render()
elif route == "analysis":
    analysis.render()
elif route == "docs":
    docs.render()
else:
    lab.render()
