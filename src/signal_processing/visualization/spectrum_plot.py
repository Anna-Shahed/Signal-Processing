"""Spectrum plotting with Matplotlib (Magnitude / Phase / Power)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..core import Spectrum
from .theme import MIDNIGHT, apply_matplotlib_theme


def _freqs(spectrum: Spectrum) -> np.ndarray:
    return np.asarray(spectrum.frequencies, dtype=float)


def _mag(spectrum: Spectrum) -> np.ndarray:
    return np.abs(np.asarray(spectrum.values, dtype=complex))


def plot_magnitude_spectrum(
    spectrum: Spectrum,
    *,
    ax: Axes | None = None,
    db: bool = False,
    title: str | None = None,
    color: str | None = None,
    vmin_db: float = -120.0,
) -> tuple[Figure, Axes]:
    """Plot magnitude versus frequency.

    dB uses the amplitude reference ``20 * log10(|X|)``. The values are
    expected to already be amplitude-corrected (window coherent gain).
    """
    apply_matplotlib_theme()
    if ax is None:
        _, ax = plt.subplots()
    fig = ax.figure

    freqs = _freqs(spectrum)
    mag = _mag(spectrum)
    if db:
        mag = np.where(mag > 0.0, 20.0 * np.log10(mag), vmin_db)
        ax.set_ylabel("Magnitude (dB, ref 1)")
    else:
        ax.set_ylabel("Magnitude")

    ax.plot(freqs, mag, color=color or MIDNIGHT["accent_violet"], linewidth=1.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_xlim(freqs[0], freqs[-1])
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def plot_phase_spectrum(
    spectrum: Spectrum,
    *,
    ax: Axes | None = None,
    unwrap: bool = False,
    title: str | None = None,
    color: str | None = None,
) -> tuple[Figure, Axes]:
    """Plot phase versus frequency (radians)."""
    apply_matplotlib_theme()
    if ax is None:
        _, ax = plt.subplots()
    fig = ax.figure

    freqs = _freqs(spectrum)
    phase = np.angle(np.asarray(spectrum.values, dtype=complex))
    if unwrap:
        phase = np.unwrap(phase)

    ax.plot(freqs, phase, color=color or MIDNIGHT["accent_amber"], linewidth=1.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Phase (rad)")
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def plot_power_spectrum(
    spectrum: Spectrum,
    *,
    ax: Axes | None = None,
    db: bool = False,
    title: str | None = None,
    color: str | None = None,
) -> tuple[Figure, Axes]:
    """Plot power (|X|^2) versus frequency.

    Power dB uses ``10 * log10(|X|^2)`` — the correct reference for a power
    quantity (distinct from the magnitude reference above).
    """
    apply_matplotlib_theme()
    if ax is None:
        _, ax = plt.subplots()
    fig = ax.figure

    freqs = _freqs(spectrum)
    power = _mag(spectrum) ** 2
    if db:
        power = np.where(power > 0.0, 10.0 * np.log10(power), -300.0)
        ax.set_ylabel("Power (dB)")
    else:
        ax.set_ylabel("Power")

    ax.plot(freqs, power, color=color or MIDNIGHT["accent_blue"], linewidth=1.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_xlim(freqs[0], freqs[-1])
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def plot_spectrum(
    spectrum: Spectrum,
    *,
    db: bool = False,
    include_phase: bool = True,
    title: str | None = None,
) -> tuple[Figure, list[Axes]]:
    """Stacked magnitude (+ optional phase) spectrum figure."""
    apply_matplotlib_theme()
    n = 2 if include_phase else 1
    fig, axes = plt.subplots(n, 1, figsize=(9, 2.6 * n), sharex=True, squeeze=False)
    axes = [ax for row in axes for ax in row]
    plot_magnitude_spectrum(spectrum, ax=axes[0], db=db)
    if include_phase:
        plot_phase_spectrum(spectrum, ax=axes[1])
    if title:
        fig.suptitle(title, y=0.99)
    fig.tight_layout()
    return fig, axes
