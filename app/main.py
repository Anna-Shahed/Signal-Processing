from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
for _p in (_REPO_ROOT / "src", _REPO_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from app import components as ui
from app.engine import run_task  
from app.state import init_state, set as set_state
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
        parts.append(f'<span class="{"stage active" if i == active_index else "stage"}">{s}</span>')
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

init_state()

_css_path = Path(__file__).parent / "styles.css"
css = _css_path.read_text(encoding="utf-8") if _css_path.exists() else ""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.markdown(
    """<style>
    :root {
      --glass-bg: rgba(18, 18, 24, 0.65);
      --glass-border: rgba(255, 255, 255, 0.12);
      --glass-blur: blur(24px) saturate(180%);
      --radius: 18px;
      --ease: cubic-bezier(0.16, 1, 0.3, 1);
      --ink: #e8e8ea;
      --ink-2: #9a9aa3;
      --ink-3: #63636e;
      --neon-cyan: #22d3ee;
      --neon-violet: #a78bfa;
      --neon-emerald: #34d399;
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
              "Helvetica Neue", Arial, sans-serif;
      --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace;
    }
    html, body, .stApp, p, span, label, div, h1, h2, h3, h4 {
      font-family: var(--font) !important;
      color: var(--ink);
      -webkit-font-smoothing: antialiased;
    }
    [data-testid="stAppViewContainer"] { background: #000; }
    .block-container { max-width: 100% !important; padding-bottom: 5rem !important; }

    /* ---- kill vertical text collapse / column crush ---- */
    .sp-section-title { white-space: nowrap !important; letter-spacing: 0.14em; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem; }
    [data-testid="column"] { min-width: 0; }

    /* ---- glass panels ---- */
    .sp-glass, .sp-rail, .sp-topbar, .sp-metric, .sp-event, .sp-pipeline,
    .stButton > button, [data-testid="stDownloadButton"] button,
    .stTextInput input, [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stExpander"], [data-testid="stDialog"] {
      background: var(--glass-bg) !important;
      -webkit-backdrop-filter: var(--glass-blur) !important;
      backdrop-filter: var(--glass-blur) !important;
      border: 1px solid var(--glass-border) !important;
      border-radius: var(--radius) !important;
      box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08);
    }
    .sp-rail { padding: 1rem; }

    /* ---- micro-interactions ---- */
    .stButton > button, [data-testid="stDownloadButton"] button,
    [data-testid="stExpander"], .sp-metric {
      transition: transform 0.3s var(--ease), background 0.3s var(--ease),
                  box-shadow 0.3s var(--ease), font-weight 0.3s var(--ease) !important;
    }
    .stButton > button:hover {
      background: rgba(34, 211, 238, 0.10) !important;
      border-color: rgba(34, 211, 238, 0.35) !important;
      transform: translateY(-2px);
      box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    }
    .stButton > button:active { transform: translateY(0) scale(0.98); }

    /* ---- typography hierarchy ---- */
    .sp-brand, .sp-section-title, .sp-readout small, .sp-metric .label,
    .mono, code, kbd { font-family: var(--mono) !important; letter-spacing: 0.1em; }
    .sp-section-title { color: var(--ink-3) !important; font-size: 11px;
                         text-transform: uppercase; border-bottom: 1px solid var(--glass-border);
                         padding-bottom: 0.5rem; margin-bottom: 0.75rem; }
    .sp-readout { font-size: 14px; line-height: 1.6; color: var(--ink-2); }
    .sp-readout strong { color: var(--ink); font-weight: 600; }
    .sp-readout.alert strong { color: var(--neon-cyan); }
    .sp-metric .value { color: var(--neon-cyan); font-family: var(--mono); font-size: 15px; }
    .sp-pipeline .stage.active { color: var(--neon-emerald); border-color: var(--neon-emerald); }
    .sp-event { border-left: 1px solid var(--neon-violet); }

    /* ---- global spatial footer ---- */
    .sp-footer {
      position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
      padding: 0.45rem 1.3rem; border-radius: 999px; z-index: 9999;
      background: var(--glass-bg);
      -webkit-backdrop-filter: var(--glass-blur);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      font-family: var(--font); font-size: 12px; color: var(--ink-3);
      letter-spacing: 0.05em; white-space: nowrap;
      transition: color 0.3s var(--ease);
    }
    .sp-footer:hover { color: var(--ink); }
    .sp-footer a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--glass-border); }
    .sp-footer a:hover { border-bottom-color: var(--ink-2); }

    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; transform: none !important; }
    }
    </style>""",
    unsafe_allow_html=True,
)

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
        current = st.session_state.get("active_tab", "lab")
        cols = st.columns(len(items))
        for col, (route, label) in zip(cols, items):
            with col:
                if st.button(label, key=f"nav_{route}",
                             type="primary" if route == current else "secondary",
                             use_container_width=True):
                    set_state("active_tab", route)
                    st.rerun()

    ui.render_top_nav = _fallback_top_nav

ui.render_top_nav()

try:
    route = st.session_state.get("active_tab", "lab")
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
except Exception as exc:  # noqa: BLE001
    st.error(f"The {route or 'lab'} view failed: {exc}")

st.markdown(
    '<div class="sp-footer">@github · <a href="https://github.com/anna-shahed" '
    'target="_blank">Anna-Shahed</a></div>',
    unsafe_allow_html=True,
)
