from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ..core import Spectrogram
from .mpl import use_editorial_style

MIDNIGHT = LinearSegmentedColormap.from_list(
    "midnight",
    ["#000000", "#0a1020", "#16294a", "#3e5f8f", "#9db6d6", "#e8ecf2"],
)

def plot_spectrogram(
    spectrogram: Spectrogram,
    *,
    db: bool = True,
    floor_db: float = -80.0,
    cmap: str | object = "midnight",
    ax=None,
    figsize: tuple[float, float] = (10, 4.6),
):
    """Plot the spectrogram on black with a hand-built ice ramp.

    Faint structure survives in dark mode while loud bands stay controlled;
    the floor is explicit and user-adjustable.
    """
    use_editorial_style()
    colormap = MIDNIGHT if cmap == "midnight" else cmap
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    data = np.abs(spectrogram.values)
    if db:
        with np.errstate(divide="ignore"):
            data = 20.0 * np.log10(data + 1e-12)
        data = np.clip(data, floor_db, None)
        label = "magnitude (dB)"
    else:
        label = "magnitude"

    # values assumed (frames, freq_bins); transpose -> (freq_bins, frames)
    extent = [spectrogram.times[0], spectrogram.times[-1],
              spectrogram.frequencies[0], spectrogram.frequencies[-1]]
    im = ax.imshow(data.T, aspect="auto", origin="lower", extent=extent,
                   cmap=colormap, interpolation="nearest")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("frequency (Hz)")
    ax.set_title(label, loc="left", fontsize=9)

    cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.035)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7, colors="#63636e")
    fig.tight_layout()
    return fig
