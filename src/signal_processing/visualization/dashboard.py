"""Composite scientific dashboard and filter-response figures."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..core import Signal, Spectrum, Spectrogram
from .signal_plot import plot_signal
from .spectrogram_plot import plot_spectrogram
from .spectrum_plot import plot_magnitude_spectrum
from .theme import MIDNIGHT, apply_matplotlib_theme


def plot_dashboard(
    signal: Signal,
    *,
    spectrum: Spectrum | None = None,
    spectrogram: Spectrogram | None = None,
    events: list | None = None,
    title: str | None = None,
    db: bool = True,
) -> tuple[Figure, list[Axes]]:
    """Stacked dashboard: waveform (+ events), magnitude spectrum, spectrogram."""
    apply_matplotlib_theme()
    n = 1 + (spectrum is not None) + (spectrogram is not None)
    fig, axes = plt.subplots(n, 1, figsize=(11, 2.9 * n), squeeze=False)
    axes = [ax for row in axes for ax in row]

    i = 0
    plot_signal(signal, ax=axes[i], events=events, title=title or "Waveform", legend=False)
    i += 1
    if spectrum is not None:
        plot_magnitude_spectrum(spectrum, ax=axes[i], db=db, title="Magnitude spectrum")
        i += 1
    if spectrogram is not None:
        plot_spectrogram(spectrogram, ax=axes[i], db=True, title="Spectrogram")
        i += 1

    fig.tight_layout()
    return fig, axes


def plot_filter_response(
    b,
    a=None,
    *,
    sampling_rate: float = 1.0,
    title: str = "Filter frequency response",
) -> tuple[Figure, tuple[Axes, Axes]]:
    """Magnitude (dB) and phase (deg) response of filter coefficients.

    Uses ``scipy.signal.freqz`` with 4096 frequency points and a frequency
    axis calibrated in hertz.
    """
    from scipy.signal import freqz

    apply_matplotlib_theme()
    b = np.asarray(b, dtype=float)
    a = np.asarray([1.0] if a is None else a, dtype=float)

    w, h = freqz(b, a, worN=4096, fs=float(sampling_rate))
    mag_db = 20.0 * np.log10(np.maximum(np.abs(h), 1e-12))
    phase = np.angle(h, deg=True)

    fig, (axm, axp) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True)
    axm.plot(w, mag_db, color=MIDNIGHT["accent_violet"], linewidth=1.3)
    axm.set_ylabel("Magnitude (dB)")
    axm.set_title(title)
    axp.plot(w, phase, color=MIDNIGHT["accent_amber"], linewidth=1.3)
    axp.set_ylabel("Phase (deg)")
    axp.set_xlabel("Frequency (Hz)")
    fig.tight_layout()
    return fig, (axm, axp)
