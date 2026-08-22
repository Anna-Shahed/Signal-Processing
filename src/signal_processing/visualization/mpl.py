"""Shared editorial Matplotlib style for exported figures.

from __future__ import annotations

import matplotlib as mpl

from .theme import (
    ACCENT,
    EVENT,
    HAIRLINE,
    HAIRLINE_STRONG,
    INK,
    INK_2,
    INK_3,
    MONO,
    SANS,
)

_APPLIED = False

def use_editorial_style() -> None:
    """Apply the midnight rcParams once per process."""
    global _APPLIED
    if _APPLIED:
        return
    mpl.rcParams.update({
        "figure.facecolor": "#000000",
        "axes.facecolor": "#000000",
        "savefig.facecolor": "#000000",
        "text.color": INK,
        "axes.edgecolor": HAIRLINE_STRONG,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "xtick.color": INK_3,
        "ytick.color": INK_3,
        "grid.color": HAIRLINE,
        "grid.linewidth": 0.6,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "font.family": SANS,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "figure.dpi": 120,
        "axes.prop_cycle": mpl.cycler(color=[INK, ACCENT, EVENT, "#8a8f9d", "#5c9d8c"]),
    })
    _APPLIED = True

def mono_annotation(ax, text: str) -> None:
    """Small mono technical label floating above an axes (metadata line)."""
    ax.text(0.0, 1.03, text, transform=ax.transAxes,
            family=MONO, fontsize=7.5, color=INK_3, va="bottom")
