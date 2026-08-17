"""Visualization: Midnight-theme Matplotlib and Plotly plotting."""

from __future__ import annotations

from .dashboard import plot_dashboard, plot_filter_response
from .signal_plot import plot_signal
from .spectrogram_plot import plot_spectrogram
from .spectrum_plot import (
    plot_magnitude_spectrum,
    plot_phase_spectrum,
    plot_power_spectrum,
    plot_spectrum,
)
from .theme import (
    MIDNIGHT,
    SERIES,
    SPECTROGRAM_CMAP,
    apply_matplotlib_theme,
    new_plotly_figure,
    plotly_template,
)

__all__ = [
    "MIDNIGHT",
    "SERIES",
    "SPECTROGRAM_CMAP",
    "apply_matplotlib_theme",
    "new_plotly_figure",
    "plotly_template",
    "plot_signal",
    "plot_magnitude_spectrum",
    "plot_phase_spectrum",
    "plot_power_spectrum",
    "plot_spectrum",
    "plot_spectrogram",
    "plot_dashboard",
    "plot_filter_response",
]
