
import matplotlib.pyplot as plt
import plotly.graph_objects as go

SERIES = [
    MIDNIGHT["accent"],
    MIDNIGHT["accent_violet"],
    MIDNIGHT["accent_amber"],
    MIDNIGHT["accent_emerald"],
    MIDNIGHT["accent_rose"],
    MIDNIGHT["accent_blue"],
]

FONT_STACK = ["Inter", "IBM Plex Sans", "Segoe UI", "DejaVu Sans", "sans-serif"]
MONO_STACK = [
    "JetBrains Mono", "IBM Plex Mono", "SFMono-Regular",
    "Menlo", "Consolas", "DejaVu Sans Mono", "monospace",
]

SPECTROGRAM_CMAP = [
    "#07070c", "#0d1424", "#142442", "#1d3a66", "#20528c", "#1f6fb0",
    "#22a6cf", "#38d6e8", "#8cf0f5", "#e0fdfb", "#fde68a", "#f59e0b",
]


def apply_matplotlib_theme() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": MIDNIGHT["background"],
            "figure.edgecolor": MIDNIGHT["background"],
            "savefig.facecolor": MIDNIGHT["background"],
            "savefig.edgecolor": MIDNIGHT["background"],
            "axes.facecolor": MIDNIGHT["surface"],
            "axes.edgecolor": MIDNIGHT["border"],
            "axes.labelcolor": MIDNIGHT["text"],
            "axes.titlecolor": MIDNIGHT["text"],
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MIDNIGHT["muted"],
            "ytick.color": MIDNIGHT["muted"],
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "grid.color": MIDNIGHT["grid"],
            "grid.alpha": 0.55,
            "grid.linewidth": 0.7,
            "text.color": MIDNIGHT["text"],
            "font.family": "sans-serif",
            "font.sans-serif": FONT_STACK,
            "mathtext.fontset": "dejavusans",
            "legend.facecolor": MIDNIGHT["surface_alt"],
            "legend.edgecolor": MIDNIGHT["border"],
            "legend.labelcolor": MIDNIGHT["text"],
            "legend.framealpha": 0.92,
            "figure.dpi": 110,
            "savefig.dpi": 160,
            "lines.linewidth": 1.4,
            "lines.markersize": 4.0,
        }
    )


def plotly_template() -> dict:
    return {
        "layout": {
            "paper_bgcolor": MIDNIGHT["background"],
            "plot_bgcolor": MIDNIGHT["surface"],
            "font": {
                "family": ", ".join(FONT_STACK),
                "color": MIDNIGHT["text"],
                "size": 12,
            },
            "title": {"font": {"size": 14, "color": MIDNIGHT["text"]}, "x": 0.02},
            "xaxis": {
                "gridcolor": MIDNIGHT["grid"],
                "zerolinecolor": MIDNIGHT["faint"],
                "linecolor": MIDNIGHT["border"],
                "tickcolor": MIDNIGHT["faint"],
                "tickfont": {"color": MIDNIGHT["muted"]},
                "titlefont": {"color": MIDNIGHT["muted"]},
                "showline": True,
            },
            "yaxis": {
                "gridcolor": MIDNIGHT["grid"],
                "zerolinecolor": MIDNIGHT["faint"],
                "linecolor": MIDNIGHT["border"],
                "tickcolor": MIDNIGHT["faint"],
                "tickfont": {"color": MIDNIGHT["muted"]},
                "titlefont": {"color": MIDNIGHT["muted"]},
                "showline": True,
            },
            "coloraxis": {
                "colorbar": {"tickfont": {"color": MIDNIGHT["muted"]}, "outlinewidth": 0}
            },
            "legend": {
                "bgcolor": MIDNIGHT["surface_alt"],
                "bordercolor": MIDNIGHT["border"],
                "font": {"color": MIDNIGHT["text"]},
            },
            "hoverlabel": {
                "bgcolor": MIDNIGHT["surface_alt"],
                "bordercolor": MIDNIGHT["border"],
                "font": {"color": MIDNIGHT["text"], "family": ", ".join(MONO_STACK)},
            },
            "margin": {"l": 56, "r": 24, "t": 44, "b": 44},
        }
    }


def new_plotly_figure() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(template=plotly_template())
    return fig

def as_spectrogram_colorscale() -> list[list[float | str]]:
    n = len(SPECTROGRAM_CMAP)
    return [[i / (n - 1), color] for i, color in enumerate(SPECTROGRAM_CMAP)]
