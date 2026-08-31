from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from .theme import ACCENT, EVENT, HAIRLINE, HAIRLINE_STRONG, INK, INK_2, INK_3, MONO

_FONT = '"Apple Garamond", "EB Garamond", "Garamond", Georgia, serif'
_MONO = MONO

_AXIS: dict[str, Any] = {
    "showgrid": True,
    "gridcolor": HAIRLINE,
    "gridwidth": 0.6,
    "zeroline": False,
    "linecolor": HAIRLINE_STRONG,
    "linewidth": 1,
    "tickcolor": HAIRLINE_STRONG,
    "tickfont": {"family": _MONO, "color": INK_3, "size": 10},
    "titlefont": {"family": _FONT, "color": INK_2, "size": 13},
    "automargin": True,
}

_BASE_LAYOUT: dict[str, Any] = {
    "template": None,
    "paper_bgcolor": "#000000",
    "plot_bgcolor": "#000000",
    "font": {"family": _FONT, "color": INK, "size": 13},
    "margin": {"l": 48, "r": 16, "t": 44, "b": 40},
    "showlegend": False,
    "hoverlabel": {
        "bgcolor": "#0d0d10",
        "bordercolor": HAIRLINE_STRONG,
        "font": {"family": _MONO, "color": INK, "size": 11},
    },
    "xaxis": dict(_AXIS),
    "yaxis": dict(_AXIS),
}


def editorial_figure(layout: dict[str, Any] | None = None, **kwargs: Any) -> go.Figure:
    """Styled figure. Accepts height=, width=, title= and any layout key."""
    merged = dict(_BASE_LAYOUT)
    if kwargs.get("height") is not None:
        merged["height"] = kwargs["height"]
    if kwargs.get("width") is not None:
        merged["width"] = kwargs["width"]
    if kwargs.get("title"):
        merged["title"] = {
            "text": kwargs["title"],
            "font": {"family": _FONT, "size": 15, "color": INK},
            "x": 0,
        }
    if layout:
        for key, value in layout.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return go.Figure(layout=merged)


def trace_signal(t: Any, samples: Any, name: str = "signal", color: str = INK, width: float = 1.0) -> go.Scatter:
    return go.Scatter(
        x=t, y=samples, mode="lines", name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.4f} s<br>%{y:.4f}<extra></extra>",
    )


trace_time = trace_signal
trace_waveform = trace_signal


def trace_spectrum(frequencies: Any, magnitudes: Any, name: str = "spectrum", color: str = ACCENT, width: float = 1.0) -> go.Scatter:
    return go.Scatter(
        x=frequencies, y=magnitudes, mode="lines", name=name,
        line={"color": color, "width": width},
        hovertemplate="%{x:.1f} Hz<br>%{y:.4f}<extra></extra>",
    )


def chart(traces: Any, layout: dict[str, Any] | None = None, **kwargs: Any) -> go.Figure:
    fig = editorial_figure(layout, **kwargs)
    if isinstance(traces, list):
        fig.add_traces(traces)
    else:
        fig.add_trace(traces)
    return fig


def add_event_markers(fig: go.Figure, events: Any, **kwargs: Any) -> go.Figure:
    color = kwargs.get("color", EVENT)
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
