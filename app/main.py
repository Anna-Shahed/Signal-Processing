from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
for _p in (_REPO_ROOT / "src", _REPO_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

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

_css_path = Path(__file__).parent / "styles.css"
css = _css_path.read_text(encoding="utf-8") if _css_path.exists() else ""

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
