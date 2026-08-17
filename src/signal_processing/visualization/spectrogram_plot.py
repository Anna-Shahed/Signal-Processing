"""Spectrogram plotting with Matplotlib."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

from ..core import Spectrogram
from .theme import SPECTROGRAM_CMAP, apply_matplotlib_theme


def _magnitude(spectrogram: Spectrogram) -> np.ndarray:
    values = getattr(spectrogram, "values", None)
    if values is not None:
        return np.abs(np.asarray(values, dtype=complex))
    return np.asarray(getattr(spectrogram, "magnitude", np.zeros((1, 1))), dtype=float)


def plot_spectrogram(
    spectrogram: Spectrogram,
    *,
    ax: Axes | None = None,
    db: bool = True,
    vmin_db: float = -80.0,
    vmax_db: float | None = None,
    cmap: str | list[str] | LinearSegmentedColormap | None = None,
    show_colorbar: bool = True,
    title: str | None = None,
) -> tuple[Figure, Axes]:
    """Plot an STFT spectrogram.

    dB uses ``20 * log10(|STFT|)`` with a user-controllable floor so that
    numerical noise does not stretch the color range.
    """
    apply_matplotlib_theme()
    if ax is None:
        _, ax = plt.subplots()
    fig = ax.figure

    times = np.asarray(getattr(spectrogram, "times"), dtype=float)
    freqs = np.asarray(getattr(spectrogram, "frequencies"), dtype=float)
    mag = _magnitude(spectrogram)

    if db:
        z = 20.0 * np.log10(np.maximum(mag, 10.0 ** (vmin_db / 20.0)))
    else:
        z = mag

    if cmap is None:
        cmap = LinearSegmentedColormap.from_list("midnight", SPECTROGRAM_CMAP)

    mesh = ax.pcolormesh(times, freqs, z.T, shading="auto", cmap=cmap)
    if db and vmax_db is not None:
        mesh.set_clim(vmin_db, vmax_db)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    if title:
        ax.set_title(title)
    else:
        ax.set_title("Spectrogram")
    if show_colorbar:
        fig.colorbar(mesh, ax=ax, label="Power (dB)" if db else "Magnitude")
    fig.tight_layout()
    return fig, ax
