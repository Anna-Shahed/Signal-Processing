"""Plotly chart builders shared by the laboratory pages (Midnight theme)."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import freqz

from signal_processing.visualization.theme import (
    MIDNIGHT,
    SERIES,
    as_spectrogram_colorscale,
    new_plotly_figure,
)


def _t(signal) -> np.ndarray:
    return np.asarray(signal.time, dtype=float)


def _y(signal) -> np.ndarray:
    return np.asarray(signal.samples, dtype=float)


def waveform_chart(signal, *, events=None, height=340, name=None, color=None):
    """Waveform with optional event spans (rose translucent bands)."""
    fig = new_plotly_figure()
    fig.add_trace(go.Scatter(
        x=_t(signal),
        y=_y(signal),
        mode="lines",
        name=name or signal.name or "signal",
        line=dict(color=color or SERIES[0], width=1.5),
        hovertemplate="t=%{x:.4f} s<br>v=%{y:.4g}<extra></extra>",
    ))
    if events:
        for ev in events:
            start = float(getattr(ev, "start_time", getattr(ev, "peak_time", np.nan)))
            end = float(getattr(ev, "end_time", np.nan))
            if np.isfinite(start):
                if np.isfinite(end) and end >= start:
                    fig.add_vrect(x0=start, x1=end, fillcolor=MIDNIGHT["accent_rose"],
                                  opacity=0.10, line_width=0)
                else:
                    fig.add_vline(x=start, line_dash="dash", line_width=1,
                                  line_color=MIDNIGHT["accent_rose"])
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=16, t=28, b=36),
        xaxis_title="Time (s)",
        yaxis_title=signal.units or "Amplitude",
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig


def spectrum_chart(spectrum, *, db=False, height=340, title=None,
                   color=None, vmin_db=-120.0):
    """Magnitude spectrum; dB uses 20*log10(|X|) with the given floor."""
    fig = new_plotly_figure()
    freqs = np.asarray(spectrum.frequencies, dtype=float)
    mag = np.abs(np.asarray(spectrum.values, dtype=complex))
    if db:
        y = np.where(mag > 0.0, 20.0 * np.log10(mag), vmin_db)
        ylabel = "Magnitude (dB)"
        hover = "f=%{x:.2f} Hz<br>|X|= %{y:.2f} dB<extra></extra>"
    else:
        y = mag
        ylabel = "Magnitude"
        hover = "f=%{x:.2f} Hz<br>|X|= %{y:.4g}<extra></extra>"
    fig.add_trace(go.Scatter(
        x=freqs, y=y, mode="lines", name="magnitude",
        line=dict(color=color or SERIES[1], width=1.5),
        hovertemplate=hover,
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=16, t=28, b=36),
        xaxis_title="Frequency (Hz)",
        yaxis_title=ylabel,
        title=title or "Magnitude spectrum",
    )
    return fig


def phase_chart(spectrum, *, height=300, color=None, unwrap=False):
    """Phase spectrum in radians."""
    fig = new_plotly_figure()
    freqs = np.asarray(spectrum.frequencies, dtype=float)
    phase = np.angle(np.asarray(spectrum.values, dtype=complex))
    if unwrap:
        phase = np.unwrap(phase)
    fig.add_trace(go.Scatter(
        x=freqs, y=phase, mode="lines", name="phase",
        line=dict(color=color or SERIES[2], width=1.3),
        hovertemplate="f=%{x:.2f} Hz<br>∠ = %{y:.3f} rad<extra></extra>",
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=16, t=28, b=36),
        xaxis_title="Frequency (Hz)",
        yaxis_title="Phase (rad)",
    )
    return fig


def spectrogram_chart(spectrogram, *, db=True, height=400, vmin_db=-80.0, title=None):
    """STFT heatmap; dB uses 20*log10(|STFT|) floored at vmin_db."""
    times = np.asarray(getattr(spectrogram, "times"), dtype=float)
    freqs = np.asarray(getattr(spectrogram, "frequencies"), dtype=float)
    values = getattr(spectrogram, "values", None)
    mag = np.abs(values) if values is not None else np.asarray(getattr(spectrogram, "magnitude"))
    z = mag.T
    if db:
        z = 20.0 * np.log10(np.maximum(z, 10.0 ** (vmin_db / 20.0)))
        cbar_title = "Power (dB)"
        hover = "t=%{x:.3f} s<br>f=%{y:.1f} Hz<br>%{z:.2f} dB<extra></extra>"
    else:
        cbar_title = "Magnitude"
        hover = "t=%{x:.3f} s<br>f=%{y:.1f} Hz<br>%{z:.4g}<extra></extra>"

    fig = new_plotly_figure()
    fig.add_trace(go.Heatmap(
        x=times, y=freqs, z=z,
        colorscale=as_spectrogram_colorscale(),
        colorbar=dict(title=cbar_title, ticks="outside"),
        hovertemplate=hover,
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=16, t=28, b=36),
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        title=title or "Spectrogram",
    )
    return fig


def filter_response_chart(b, a=None, *, fs=1.0, height=440, title="Filter response"):
    """Magnitude (dB) and phase (deg) from scipy.signal.freqz at 4096 points."""
    a = np.atleast_1d([1.0] if a is None else a)
    w, h = freqz(np.asarray(b, dtype=float), np.asarray(a, dtype=float),
                 worN=4096, fs=float(fs))
    mag_db = 20.0 * np.log10(np.maximum(np.abs(h), 1e-12))
    phase = np.angle(h, deg=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Magnitude response", "Phase response"))
    fig.add_trace(go.Scatter(x=w, y=mag_db, mode="lines", name="|H(f)| (dB)",
                             line=dict(color=SERIES[1], width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=w, y=phase, mode="lines", name="∠H(f) (deg)",
                             line=dict(color=SERIES[2], width=1.5)), row=2, col=1)
    fig.update_layout(height=height, title=title, showlegend=False,
                      margin=dict(l=48, r=16, t=40, b=36))
    fig.update_xaxes(title_text="Frequency (Hz)", row=2, col=1)
    fig.update_yaxes(title_text="dB", row=1, col=1)
    fig.update_yaxes(title_text="degrees", row=2, col=1)
    return fig


def compare_chart(original, filtered, *, height=360):
    """Original vs filtered waveform overlay."""
    fig = new_plotly_figure()
    fig.add_trace(go.Scatter(x=_t(original), y=_y(original), mode="lines", name="original",
                             line=dict(color=SERIES[0], width=1.1)))
    fig.add_trace(go.Scatter(x=_t(filtered), y=_y(filtered), mode="lines", name="filtered",
                             line=dict(color=SERIES[3], width=1.5)))
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=16, t=28, b=36),
        xaxis_title="Time (s)",
        yaxis_title=original.units or "Amplitude",
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig
