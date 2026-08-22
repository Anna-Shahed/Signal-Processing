"""Editorial spectral plots: magnitude, phase, power."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ..core import Spectrum
from .mpl import use_editorial_style

def plot_spectrum(
    spectrum: Spectrum,
    *,
    kind: str = "magnitude",
    db: bool = False,
    ax=None,
    figsize: tuple[float, float] = (10, 3.6),
):
    """Plot magnitude, phase, or power on black.

    dB references are explicit: magnitude uses 20*log10(|X|),
    power uses 10*log10(|X|^2). Phase is unwrapped.
    """
    use_editorial_style()
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    f = np.asarray(spectrum.frequencies)
    values = np.asarray(spectrum.values)

    if kind == "phase":
        y = np.unwrap(np.angle(values))
        ax.plot(f, y, color="#8f9bb8", linewidth=0.9)
        ax.set_ylabel("phase (rad)")
        ax.axhline(0, color="#2a2a30", linewidth=0.6)
    elif kind == "power":
        y = (10.0 * np.log10(np.abs(values) ** 2 + 1e-12) if db
             else np.abs(values) ** 2)
        ax.plot(f, y, color="#8f9bb8", linewidth=0.9)
        ax.set_ylabel("power (dB)" if db else "power")
    else:
        with np.errstate(divide="ignore"):
            y = 20.0 * np.log10(np.abs(values) + 1e-12) if db else np.abs(values)
        ax.plot(f, y, color="#e8e8ea", linewidth=0.9)
        ax.set_ylabel("magnitude (dB)" if db else "magnitude")

    ax.set_xlabel("frequency (Hz)")
    ax.set_xlim(f[0], f[-1])
    ax.margins(x=0.01)
    fig.tight_layout()
    return fig
