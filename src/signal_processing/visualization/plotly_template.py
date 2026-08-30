from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

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

_AXIS: dict[str, Any] = {
    "showgrid": True,
    "gridcolor": HAIRLINE,
    "gridwidth": 0.6,
    "zeroline": False,
    "linecolor": HAIRLINE_STRONG,
    "linewidth": 1,
    "tickcolor": HAIRLINE_STRONG,
    "tickfont": {"family": MONO, "color": INK_3, "size": 10},
    "titlefont": {"family": SANS, "color": INK_2, "size": 11},
    "automargin": True,
}

_BASE_LAYOUT: dict[str, Any] = {
    "template": None,
    "paper_bgcolor": "#000000",
    "plot_bgcolor": "#000000",
    "font": {"family": SANS, "color": INK, "size": 12},
    "margin": {"l": 48, "r": 16, "t": 40, "b": 40},
    "showlegend": False,
    "hoverlabel": {
        "bgcolor": "#0d0d10",
        "bordercolor": HAIRLINE_STRONG,
        "font": {"family": MONO, "color": INK, "size": 11},
    },
    "xaxis": dict(_AXIS),
    "yaxis": dict(_AXIS),
}


def editorial_figure(layout: dict[str, Any] | None = None) -> go.Figure:
    """Return an empty figure pre-styled to the editorial midnight system."""
    merged = dict(_BASE_LAYOUT)
    if layout:
        for key, value in layout.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return go.Figure(layout=merged)


def trace_signal(
    t: Any,
    samples: Any,
    name: str = "signal",
    color: str = INK,
    width: float = 1.0,
) -> go.Scatter:
    """Thin white waveform trace (TIME DOMAIN)."""
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
    color: str = ACCENT,
    width: float = 1.0,
) -> go.Scatter:
    return go.Scatter(
        x=frequencies,
        y=magnitudes,
        mode="lines",
        name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.1f} Hz<br>%{y:.4f}<extra></extra>",
    )


def chart(
    traces: go.Scatter | list[go.Scatter],
    layout: dict[str, Any] | None = None,
) -> go.Figure:
    fig = editorial_figure(layout)
    if isinstance(traces, list):
        fig.add_traces(traces)
    else:
        fig.add_trace(traces)
    return fig


def add_event_markers(
    fig: go.Figure,
    events: Any,
    color: str = EVENT,
) -> go.Figure:
    for event in events:
        start = getattr(event, "start_time", None) or event.get("start_time") if isinstance(event, dict) else None
        if start is None:
            start = getattr(event, "start", None) or event.get("start")
        if start is None:
            continue
        fig.add_vline(
            x=float(start),
            line={"color": color, "width": 0.8, "dash": "dash"},
            opacity=0.7,
        )
    return fig
