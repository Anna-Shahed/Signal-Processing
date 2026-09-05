from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace'

NEON = {"cyan": "#22d3ee", "violet": "#a78bfa", "emerald": "#34d399"}
INK = "#e8e8ea"
INK_2 = "#9a9aa3"
INK_3 = "#63636e"
GRID = "rgba(255,255,255,0.05)"

_AXIS: dict[str, Any] = {
    "showgrid": True,
    "gridcolor": GRID,
    "gridwidth": 1,
    "zeroline": False,
    "linecolor": "rgba(255,255,255,0.12)",
    "linewidth": 1,
    "tickcolor": "rgba(255,255,255,0.12)",
    "tickfont": {"family": MONO, "color": INK_3, "size": 10},
    "titlefont": {"family": FONT, "color": INK_2, "size": 13},
    "automargin": True,
}

_BASE_LAYOUT: dict[str, Any] = {
    "template": None,
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": FONT, "color": INK, "size": 13},
    "margin": {"l": 48, "r": 16, "t": 44, "b": 40},
    "showlegend": False,
    "hoverlabel": {
        "bgcolor": "rgba(18,18,24,0.9)",
        "bordercolor": "rgba(255,255,255,0.12)",
        "font": {"family": MONO, "color": INK, "size": 11},
    },
    "xaxis": dict(_AXIS),
    "yaxis": dict(_AXIS),
}


def editorial_figure(layout: dict[str, Any] | None = None, **kwargs: Any) -> go.Figure:
    merged = dict(_BASE_LAYOUT)
    for key in ("height", "width"):
        if kwargs.get(key) is not None:
            merged[key] = kwargs[key]
    if kwargs.get("title"):
        merged["title"] = {"text": kwargs["title"], "font": {"family": FONT, "size": 15, "color": INK}, "x": 0}
    if layout:
        for key, value in layout.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return go.Figure(layout=merged)


def trace_signal(t: Any, samples: Any, name: str = "signal", color: str = NEON["cyan"], width: float = 1.4) -> go.Scatter:
    return go.Scatter(
        x=t, y=samples, mode="lines", name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.4f} s<br>%{y:.4f}<extra></extra>",
    )


trace_time = trace_signal
trace_waveform = trace_signal


def trace_spectrum(frequencies: Any, magnitudes: Any, name: str = "spectrum", color: str = NEON["violet"], width: float = 1.4) -> go.Scatter:
    return go.Scatter(
        x=frequencies, y=magnitudes, mode="lines", name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.1f} Hz<br>%{y:.4f}<extra></extra>",
    )


def chart(traces: Any, layout: dict[str, Any] | None = None, **kwargs: Any) -> go.Figure:
    if isinstance(traces, go.Figure):
        fig = traces
        if layout:
            fig.update_layout(layout)
        if kwargs:
            fig.update_layout(**kwargs)
        return fig
    fig = editorial_figure(layout, **kwargs)
    if isinstance(traces, list):
        fig.add_traces(traces)
    else:
        fig.add_trace(traces)
    return fig


def add_event_markers(fig: go.Figure, events: Any, **kwargs: Any) -> go.Figure:
    color = kwargs.get("color", NEON["emerald"])
    if not events:
        return fig
    for ev in events:
        if isinstance(ev, dict):
            x = ev.get("start_time") or ev.get("start") or ev.get("peak_time")
        elif isinstance(ev, (int, float, np.integer, np.floating)):
            x = float(ev)
        else:
            x = getattr(ev, "start_time", None) or getattr(ev, "start", None) or getattr(ev, "peak_time", None)
        if x is None:
            continue
        fig.add_vline(x=float(x), line={"color": color, "width": 0.8, "dash": "dash"}, opacity=0.7)
    return fig
