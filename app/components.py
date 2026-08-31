from __future__ import annotations

import streamlit as st


def render_top_nav() -> None:
    """Minimal top navigation: Signal Lab · Projects · Experiments · Analysis · Documentation."""
    st.markdown(
        '<div class="sp-topbar sp-glass"><span class="sp-brand">SIGNAL LAB<span>DSP INSTRUMENT</span></span></div>',
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


def section_header(title: str) -> None:
    """Small mono uppercase section title."""
    st.markdown(f'<div class="sp-section-title">{title}</div>', unsafe_allow_html=True)


def section_rule() -> None:
    """Thin hairline rule."""
    st.markdown('<hr class="sp-rule" />', unsafe_allow_html=True)


def metadata_row(text: str) -> None:
    """One line of monospace metadata."""
    st.markdown(f'<div class="sp-readout">{text}</div>', unsafe_allow_html=True)


def readout(label: str, value: str) -> None:
    """Label + monospace numeric readout."""
    st.markdown(
        f'<div class="sp-readout"><small>{label}</small><br /><strong>{value}</strong></div>',
        unsafe_allow_html=True,
    )


def metric(label: str, value: str) -> None:
    """Metric line: label + value + hairline."""
    st.markdown(
        f'<div class="sp-metric"><span class="label">{label}</span>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str) -> None:
    """Alias of metric (older pages may call this name)."""
    metric(label, value)


def led(status: str = "ok") -> None:
    """Small status LED: ok / warn / err."""
    st.markdown(f'<span class="sp-led {status}"></span>', unsafe_allow_html=True)


def status_led(status: str = "ok") -> None:
    """Alias of led."""
    led(status)


def pipeline_bar(stages: list[str] | None = None, active_index: int = -1) -> None:
    """INPUT → PROCESS → ANALYZE → RESULT pipeline strip."""
    if stages is None:
        stages = ["input", "process", "analyze", "result"]
    parts = []
    for i, stage in enumerate(stages):
        cls = "stage active" if i == active_index else "stage"
        parts.append(f'<span class="{cls}">{stage}</span>')
        if i < len(stages) - 1:
            parts.append('<span class="arrow">→</span>')
    st.markdown(f'<div class="sp-pipeline sp-glass">{"".join(parts)}</div>', unsafe_allow_html=True)


def event_row(text: str) -> None:
    """Translucent amber event line."""
    st.markdown(f'<div class="sp-event">{text}</div>', unsafe_allow_html=True)


def caption(text: str) -> None:
    """Small mono caption."""
    st.markdown(f'<div class="sp-readout"><small>{text}</small></div>', unsafe_allow_html=True)
