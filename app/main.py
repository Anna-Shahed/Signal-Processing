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

def _ui_readout(label: str, value: str, unit: str = "", alert: bool = False, **kwargs) -> None:
    cls = "sp-readout alert" if alert else "sp-readout"
    unit_html = f' <span style="color:#63636e">{unit}</span>' if unit else ""
    st.markdown(
        f'<div class="{cls}"><small>{label}</small><br /><strong>{value}{unit_html}</strong></div>',
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

# --- DESIGN SYSTEM: Apple Garamond + glass everywhere + hover/click motion ---
st.markdown(
    """<style>
    :root {
      --font-body: "Apple Garamond", "EB Garamond", "Garamond", Georgia, serif;
      --font-mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace;
    }
    html, body, .stApp, p, span, label, div, h1, h2, h3, h4 {
      font-family: var(--font-body) !important;
      color: #e8e8ea;
    }
    body { font-size: 15px; letter-spacing: 0.01em; }
    .sp-brand, .sp-section-title, .sp-readout small, .sp-metric .label,
    .mono, code, kbd { font-family: var(--font-mono) !important; }
    .sp-readout { font-size: 14px; line-height: 1.6; }
    .sp-readout strong { font-weight: 600; }
    .sp-readout.alert strong { color: #f2c879; }

    /* glass everywhere */
    .stButton > button, [data-testid="stDownloadButton"] button,
    .stTextInput input, [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stExpander"], [data-testid="stDialog"],
    .sp-glass, .sp-metric, .sp-event, .sp-pipeline, .sp-topbar, .sp-rail {
      background: rgba(255,255,255,0.05) !important;
      -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
      backdrop-filter: blur(18px) saturate(160%) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      box-shadow: 0 1px 12px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }
    .sp-rail { border-radius: 14px !important; padding: 0.9rem 1rem 0.6rem !important; }

    /* smaller buttons, bigger text, hover -> glass + bold, click -> press */
    .stButton > button, [data-testid="stDownloadButton"] button {
      font-family: var(--font-body) !important;
      font-size: 14px !important;
      padding: 0.30rem 0.9rem !important;
      font-weight: 400 !important;
      letter-spacing: 0.02em !important;
      text-transform: none !important;
      transition: all 0.18s ease !important;
      border-radius: 10px !important;
    }
    .stButton > button:hover {
      background: rgba(255,255,255,0.13) !important;
      font-weight: 700 !important;
      border-color: rgba(255,255,255,0.30) !important;
      transform: translateY(-1px);
    }
    .stButton > button:active { transform: translateY(0px); }

    /* math equations: italic bold serif with hover blurb */
    .sp-eq {
      font-family: var(--font-body);
      font-style: italic;
      font-weight: 700;
      font-size: 16px;
      color: #d6d6dc;
      border-bottom: 1px dashed rgba(255,255,255,0.15);
      cursor: help;
      padding: 0.15rem 0.1rem;
      transition: color 0.15s ease;
    }
    .sp-eq:hover { color: #ffffff; }
    .sp-blurb { color: #9a9aa3; font-size: 13.5px; line-height: 1.55; }

    @media (prefers-reduced-motion: reduce) {
      .stButton > button { transition: none !important; transform: none !important; }
    }
    </style>""",
    unsafe_allow_html=True,
)

init_state()

if not hasattr(ui, "render_top_nav"):
    def _fallback_top_nav() -> None:
        items = [
            ("lab", "Signal Lab"), ("projects", "Projects"),
            ("experiments", "Experiments"), ("analysis", "Analysis"),
            ("docs", "Documentation"),
        ]
        st.markdown(
            '<div class="sp-topbar sp-glass"><span class="sp-brand">SIGNAL LAB<span>DSP INSTRUMENT</span></span></div>',
            unsafe_allow_html=True,
        )
        current = st.session_state.get("route", "lab")
        cols = st.columns(len(items))
        for col, (route, label) in zip(cols, items):
            with col:
                if st.button(label, key=f"nav_{route}",
                             type="primary" if route == current else "secondary",
                             use_container_width=True):
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
