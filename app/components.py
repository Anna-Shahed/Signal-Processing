"""Editorial UI primitives — HTML strings, not cards."""

from __future__ import annotations

import streamlit as st

ROUTES = ["lab", "projects", "experiments", "analysis", "docs"]
LABELS = {
    "lab": "Signal Lab", "projects": "Projects", "experiments": "Experiments",
    "analysis": "Analysis", "docs": "Documentation",
}

def _html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)

def render_top_nav() -> None:
    active = st.session_state.get("route", "lab")
    _html('<div class="sp-topbar">'
          '<div class="sp-brand">Signal Lab<span>v0.1.0</span></div>'
          "</div>")
    cols = st.columns(len(ROUTES))
    for col, route in zip(cols, ROUTES):
        with col:
            is_active = route == active
            if st.button(
                LABELS[route],
                key=f"nav_{route}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["route"] = route
                st.rerun()
    _html('<div class="sp-rule"></div>')

def section_header(title: str) -> None:
    """Thin rule with an uppercase mono label — the only 'box' we use."""
    _html(f'<div class="sp-section"><span>{title}</span><i></i></div>')


def readout(label: str, value: str, unit: str = "", alert: bool = False) -> None:
    """Large mono value under a tiny technical label, hairline-divided."""
    _html(
        f'<div class="sp-readout{" sp-readout-alert" if alert else ""}">'
        f'<span class="sp-readout-label">{label}</span>'
        f'<span class="sp-readout-value">{value}<em>{unit}</em></span>'
        f"</div>"
    )

def led(state: str) -> str:
    return f'<span class="sp-led sp-led-{state}"></span>'

def pipeline_bar(stages: list[str] | None = None) -> None:
    """INPUT -> PROCESS -> ANALYZE -> RESULT with stage chips below."""
    nodes = ["INPUT", "PROCESS", "ANALYZE", "RESULT"]
    html = ['<div class="sp-pipeline">']
    for i, node in enumerate(nodes):
        html.append(f'<div class="sp-pipe-node">{node}</div>')
        if i < len(nodes) - 1:
            html.append('<div class="sp-pipe-arrow"></div>')
    html.append("</div>")
    _html("".join(html))
    if stages:
        chips = "".join(
            f'<span class="sp-stage">{led("done")}{s}</span>' for s in stages
        )
        _html(f'<div class="sp-stage-row">{chips}</div>')


def metadata_row(text: str) -> None:
    """Small mono meta line, e.g. 'fs=8000  N=8000  t=1.000s'."""
    _html(f'<div class="sp-meta" style="font-family:var(--mono);font-size:10px;'
          f'color:var(--ink-3);letter-spacing:0.08em;margin:0.3rem 0;">{text}</div>')
