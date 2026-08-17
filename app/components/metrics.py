"""Instrument-style metric cards and status indicators."""

from __future__ import annotations

import html as _html

import streamlit as st

from signal_processing.visualization.theme import MIDNIGHT


def metric_card(label: str, value, *, unit: str = "", accent: str | None = None,
                footnote: str | None = None) -> None:
    """A single instrument readout card with a colored top accent bar."""
    accent = accent or MIDNIGHT["accent"]
    label_h = _html.escape(str(label))
    value_h = _html.escape(str(value))
    unit_h = _html.escape(str(unit))
    footnote_h = _html.escape(str(footnote)) if footnote else ""
    html = f"""
    <div style="background:{MIDNIGHT['surface']};border:1px solid {MIDNIGHT['border']};
                border-top:2px solid {accent};border-radius:8px;padding:0.7rem 0.9rem;margin-bottom:0.5rem;">
      <div style="color:{MIDNIGHT['muted']};font-size:0.72rem;text-transform:uppercase;
                  letter-spacing:0.06em;">{label_h}</div>
      <div style="color:{accent};font-family:'JetBrains Mono',monospace;font-size:1.25rem;
                  font-weight:600;margin-top:0.15rem;">
        {value_h}<span style="color:{MIDNIGHT['muted']};font-size:0.8rem;margin-left:0.3rem;">{unit_h}</span>
      </div>
      {f'<div style="color:{MIDNIGHT["muted"]};font-size:0.72rem;margin-top:0.25rem;">{footnote_h}</div>' if footnote_h else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def metric_grid(metrics: dict, *, columns: int = 4) -> None:
    """Render a dict of ``label -> (value, unit)`` (or plain value) as cards."""
    items = list(metrics.items())
    for i in range(0, len(items), columns):
        cols = st.columns(columns)
        for j in range(columns):
            idx = i + j
            if idx >= len(items):
                cols[j].empty()
                continue
            label, entry = items[idx]
            if isinstance(entry, tuple):
                value, unit = entry
            else:
                value, unit = entry, ""
            with cols[j]:
                metric_card(label, value, unit=unit)


def status_led(text: str, *, ok: bool = True) -> None:
    """A small glowing status indicator (emerald = nominal, rose = alarm)."""
    color = MIDNIGHT["accent_emerald"] if ok else MIDNIGHT["accent_rose"]
    st.markdown(
        f"""<span style="display:inline-flex;align-items:center;gap:0.4rem;
        color:{MIDNIGHT['muted']};font-size:0.78rem;">
        <span style="width:8px;height:8px;border-radius:50%;background:{color};
        box-shadow:0 0 6px {color};display:inline-block;"></span>
        {_html.escape(str(text))}</span>""",
        unsafe_allow_html=True,
    )
