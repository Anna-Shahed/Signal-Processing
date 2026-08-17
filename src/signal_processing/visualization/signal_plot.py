"""Waveform plotting with Matplotlib."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..core import Event, Signal
from .theme import MIDNIGHT, apply_matplotlib_theme


def plot_signal(
    signal: Signal,
    *,
    ax: Axes | None = None,
    events: Iterable[Event] | None = None,
    title: str | None = None,
    color: str | None = None,
    linewidth: float = 1.2,
    event_color: str | None = None,
    legend: bool = True,
) -> tuple[Figure, Axes]:
    """Plot a waveform with optional event markers (rose bands / dashed lines).

    Returns
    -------
    (fig, ax)
    """
    apply_matplotlib_theme()
    if ax is None:
        _, ax = plt.subplots()
    fig = ax.figure

    time = np.asarray(signal.time, dtype=float)
    samples = np.asarray(signal.samples, dtype=float)
    ax.plot(
        time,
        samples,
        color=color or MIDNIGHT["accent"],
        linewidth=linewidth,
        label=signal.name or "signal",
        zorder=3,
    )

    if events:
        ev_color = event_color or MIDNIGHT["accent_rose"]
        for ev in events:
            start = float(getattr(ev, "start_time", getattr(ev, "peak_time", np.nan)))
            end = float(getattr(ev, "end_time", np.nan))
            if np.isfinite(start) and np.isfinite(end) and end >= start:
                ax.axvspan(start, end, color=ev_color, alpha=0.12, zorder=1)
            elif np.isfinite(start):
                ax.axvline(
                    start, color=ev_color, alpha=0.5, linestyle="--",
                    linewidth=1.0, zorder=2,
                )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(signal.units or "Amplitude")
    if title:
        ax.set_title(title)
    if legend:
        ax.legend(loc="upper right", frameon=True)
    ax.margins(x=0.01)
    fig.tight_layout()
    return fig, ax
