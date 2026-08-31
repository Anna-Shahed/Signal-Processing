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

def _ui_section_header(title: str) -> None:
    st.markdown(f'<div class="sp-section-title">{title}</div>', unsafe_allow_html=True)

def _ui_metadata_row(text: str) -> None:
    st.markdown(f'<div class="sp-readout">{text}</div>', unsafe_allow_html=True)

def _ui_readout(label: str, value: str) -> None:
    st.markdown(
        f'<div class="sp-readout"><small>{label}</small><br /><strong>{value}</strong></div>',
        unsafe_allow_html=True,
    )

def _ui_metric(label: str, value: str) -> None:
    st.markdown(
        f'<div class="sp-metric"><span class="label">{label}</span>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )

def _ui_led(status: str = "ok") -> None:
    st.markdown(f'<span class="sp-led {status}"></span>', unsafe_allow_html=True)

def _ui_pipeline_bar(stages=None, active_index: int = -1) -> None:
    if stages is None:
        stages = ["input", "process", "analyze", "result"]
    parts = []
    for i, s in enumerate(stages):
        parts.append(
            f'<span class="{"stage active" if i == active_index else "stage"}">{s}</span>'
        )
        if i < len(stages) - 1:
            parts.append('<span class="arrow">→</span>')
    st.markdown(f'<div class="sp-pipeline sp-glass">{"".join(parts)}</div>', unsafe_allow_html=True)

def _ui_event_row(text: str) -> None:
    st.markdown(f'<div class="sp-event">{text}</div>', unsafe_allow_html=True)

for _n, _f in {
    "section_header": _ui_section_header,
    "metadata_row": _ui_metadata_row,
    "readout": _ui_readout,
    "metric": _ui_metric,
    "led": _ui_led,
    "event_row": _ui_event_row,
}.items():
    if not hasattr(ui, _n):
        setattr(ui, _n, _f)
if not hasattr(ui, "pipeline_bar"):
    ui.pipeline_bar = _ui_pipeline_bar

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

st.markdown(
    """<style>
    .stButton > button, [data-testid="stDownloadButton"] button,
    .stTextInput input, [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stExpander"], [data-testid="stDialog"], .sp-glass {
      background: rgba(255,255,255,0.05) !important;
      -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
      backdrop-filter: blur(18px) saturate(160%) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      box-shadow: 0 1px 12px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }
    .stButton > button:hover {
      background: rgba(255,255,255,0.10) !important;
      border-color: rgba(255,255,255,0.18) !important;
    }
    </style>""",
    unsafe_allow_html=True,
)

init_state()

if not hasattr(ui, "render_top_nav"):
    def _fallback_top_nav() -> None:
        import streamlit as st

        st.markdown(
            '<div class="sp-topbar"><span class="sp-brand">SIGNAL LAB<span>DSP INSTRUMENT</span></span></div>',
            unsafe_allow_html=True,
        )
        items = [
            ("lab", "Signal Lab"),
            ("projects", "Projects"),
            ("experiments", "Experiments"),
            ("analysis", "Analysis"),
            ("docs", "Documentation"),
        ]
        current = st.session_state.get("route", "lab")
        cols = st.columns(len(items))
        for col, (route, label) in zip(cols, items):
            with col:
                if st.button(
                    label,
                    key=f"nav_{route}",
                    type="primary" if route == current else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["route"] = route
                    st.rerun()

    ui.render_top_nav = _fallback_top_nav

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
