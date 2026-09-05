from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import streamlit as st

try:  
    from .theme import ( 
        ACCENT,
        EVENT,
        HAIRLINE,
        HAIRLINE_STRONG,
        INK,
        INK_2,
        INK_3,
        MONO,
        SANS,
    )
except Exception: 
    ACCENT = "#8f9bb8"
    EVENT = "#f2c879"
    HAIRLINE = "rgba(255,255,255,0.05)"
    HAIRLINE_STRONG = "rgba(255,255,255,0.10)"
    INK = "#e8e8ea"
    INK_2 = "#9a9aa3"
    INK_3 = "#63636e"
    MONO = 'ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace'
    SANS = ('-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", '
            '"Helvetica Neue", Arial, sans-serif')

NEON_CYAN = "#22d3ee"
NEON_VIOLET = "#a78bfa"
NEON_EMERALD = "#34d399"
NEON_AMBER = "#f2c879"

_AXIS: dict[str, Any] = {
    "showgrid": True,
    "gridcolor": HAIRLINE,
    "gridwidth": 0.5,
    "zeroline": False,
    "linecolor": HAIRLINE_STRONG,
    "linewidth": 1,
    "tickcolor": HAIRLINE_STRONG,
    "tickfont": {"family": MONO, "color": INK_3, "size": 10},
    "title": {"font": {"family": SANS, "color": INK_2, "size": 12}},
    "automargin": True,
}

_BASE_LAYOUT: dict[str, Any] = {
    "template": None,
    "paper_bgcolor": "rgba(0,0,0,0)",  
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": SANS, "color": INK, "size": 13},
    "margin": {"l": 56, "r": 20, "t": 32, "b": 48},
    "showlegend": False,
    "hoverlabel": {
        "bgcolor": "rgba(18,18,24,0.92)",
        "bordercolor": HAIRLINE_STRONG,
        "font": {"family": MONO, "color": INK, "size": 11},
    },
    "xaxis": dict(_AXIS),
    "yaxis": dict(_AXIS),
    "colorway": [NEON_CYAN, NEON_VIOLET, NEON_EMERALD, NEON_AMBER],
}


def editorial_figure(
    layout: dict[str, Any] | None = None,
    **overrides: Any,
) -> go.Figure:
    """Return an empty figure pre-styled to the spatial dark theme.

    ``editorial_figure(height=300)`` and ``editorial_figure({"height": 300})``
    both work — extra kwargs are merged straight into the layout.
    """
    merged: dict[str, Any] = {k: (dict(v) if isinstance(v, dict) else v)
                              for k, v in _BASE_LAYOUT.items()}
    for src in (layout or {}, overrides):
        for key, value in src.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return go.Figure(layout=merged)


def chart(fig: go.Figure, height: int | None = None) -> None:
    """Render a figure full-width, transparent, responsive, no modebar noise."""
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )


def trace_signal(
    t: Any,
    samples: Any,
    name: str = "signal",
    color: str = NEON_CYAN,
    width: float = 1.2,
) -> go.Scatter:
    """Thin neon waveform trace (time domain)."""
    return go.Scatter(
        x=t,
        y=samples,
        mode="lines",
        name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.4f} s<br>%{y:.4f}<extra></extra>",
    )

trace_time = trace_signal
trace_waveform = trace_signal


def trace_spectrum(
    frequencies: Any,
    magnitudes: Any,
    name: str = "spectrum",
    color: str = NEON_VIOLET,
    width: float = 1.2,
) -> go.Scatter:
    return go.Scatter(
        x=frequencies,
        y=magnitudes,
        mode="lines",
        name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.2f} Hz<br>%{y:.4f}<extra></extra>",
    )


def trace_spectrogram(
    frequencies: Any,
    times: Any,
    values: Any,
    name: str = "spectrogram",
    colorscale: str = "Viridis",
) -> go.Heatmap:
    """Spectrogram heatmap trace."""
    return go.Heatmap(
        x=times,
        y=frequencies,
        z=values,
        name=name,
        colorscale=colorscale,
        colorbar={"outlinewidth": 0, "thickness": 10},
    )


def add_event_markers(
    fig: go.Figure,
    events: Any,
    height: float | None = None,
    color: str = NEON_AMBER,
    width: float = 1,
) -> go.Figure:
   
    times: list[float] = []
    for ev in events or []:
        if hasattr(ev, "start_time"):
            times.append(float(ev.start_time))
        else:
            times.append(float(ev))
    for t in times:
        fig.add_vline(
            x=t,
            line_color=color,
            line_width=width,
            line_dash="dash",
            opacity=0.65,
        )
    if height is not None:
        fig.update_layout(height=height)
    return fig
