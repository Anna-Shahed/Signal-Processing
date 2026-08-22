"""Editorial waveform plots for static export."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ..core import Event, Signal
from .mpl import use_editorial_style


def plot_signal(
    signal: Signal,
    *,
    events: list[Event] | None = None,
    unit: str | None = None,
    ax=None,
    figsize: tuple[float, float] = (10, 3.6),
):
    """Plot a waveform on black in a thin white line.

    Event intervals render as faint amber bands with dashed edges — the only
    color allowed in the time domain.
    """
    use_editorial_style()
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    t = np.arange(signal.n_samples) / signal.sampling_rate
    ax.plot(t, signal.samples, color="#e8e8ea", linewidth=0.9)

    if events:
        for ev in events:
            ax.axvspan(ev.start, ev.end, color="#f2c879", alpha=0.08)
            ax.axvline(ev.start, color="#f2c879", linewidth=0.6,
                       linestyle="--", alpha=0.6)
            ax.axvline(ev.end, color="#f2c879", linewidth=0.6,
                       linestyle="--", alpha=0.6)

    ax.set_xlabel("time (s)")
    ax.set_ylabel(unit or signal.units or "amplitude")
    ax.set_title(signal.name or "signal", loc="left", fontsize=11)
    ax.margins(x=0.01)
    fig.tight_layout()
    return fig
