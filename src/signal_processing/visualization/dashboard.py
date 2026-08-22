"""ays unchanged.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ..core import AnalysisResult, Event, Signal, Spectrum, Spectrogram
from .mpl import mono_annotation, use_editorial_style
from .signal_plot import plot_signal
from .spectrogram_plot import plot_spectrogram
from .spectrum_plot import plot_spectrum


def plot_dashboard(
    signal: Signal,
    *,
    spectrum: Spectrum | None = None,
    spectrogram: Spectrogram | None = None,
    analysis: AnalysisResult | None = None,
    events: list[Event] | None = None,
    figsize: tuple[float, float] = (11, 7.5),
):
    """Compose waveform + spectrum (+ spectrogram) on one black figure."""
    use_editorial_style()
    n_rows = 3 if spectrogram is not None else 2
    ratios = [2, 1, 1.4] if n_rows == 3 else [2, 1]
    fig, axes = plt.subplots(
        n_rows, 1, figsize=figsize,
        gridspec_kw={"height_ratios": ratios, "hspace": 0.5},
    )
    axes = np.atleast_1d(axes)

    plot_signal(signal, events=events, ax=axes[0])

    spec = spectrum
    if spec is None and spectrogram is None:
        from ..transforms.fft import fft
        spec = fft(signal, one_sided=True)
    if spec is not None:
        plot_spectrum(spec, kind="magnitude", db=True, ax=axes[1])
        axes[1].set_title("magnitude (dB)", loc="left", fontsize=9)

    if spectrogram is not None:
        plot_spectrogram(spectrogram, ax=axes[2])

    if analysis is not None:
        m = analysis.metrics
        text = (f"dom={m.get('dominant_frequency', float('nan')):.1f}Hz  "
                f"rms={m.get('rms', float('nan')):.4f}  "
                f"snr={m.get('snr_db', float('nan')):.1f}dB")
        mono_annotation(axes[0], text)

    fig.tight_layout()
    return fig

def plot_filter_response(
    b,
    a=None,
    *,
    fs: float = 2.0,
    n: int = 4096,
    figsize: tuple[float, float] = (10, 4.2),
):
    from scipy.signal import freqz

    use_editorial_style()
    w, h = freqz(b, a, worN=n)
    f = w / np.pi * (fs / 2.0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.semilogx(f, 20.0 * np.log10(np.abs(h) + 1e-12),
                color="#e8e8ea", linewidth=0.9)
    ax.axhline(-3.0, color="#2a2a30", linewidth=0.6, linestyle="--")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("magnitude (dB)")
    ax.set_xlim(f[1], f[-1])
    ax.set_ylim(-80.0, 5.0)

    ax2 = ax.twinx()
    ax2.plot(f, np.unwrap(np.angle(h)), color="#8f9bb8", linewidth=0.7)
    ax2.set_ylabel("phase (rad)")
    ax2.grid(False)
    ax2.tick_params(colors="#63636e", labelsize=8)
    ax2.spines["top"].set_visible(False)

    fig.tight_layout()
    return fig
