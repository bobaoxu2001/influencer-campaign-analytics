"""
Shared utility functions for visualization and formatting.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plotly.express as px
import plotly.graph_objects as go


# Color palette — modern, professional
COLORS = {
    "primary": "#2563EB",
    "secondary": "#7C3AED",
    "accent": "#F59E0B",
    "success": "#10B981",
    "danger": "#EF4444",
    "neutral": "#6B7280",
    "bg": "#F9FAFB",
    "text": "#111827",
}

TIER_ORDER = ["nano", "micro", "mid", "macro", "mega"]
TIER_COLORS = ["#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]


def set_plot_style():
    """Apply clean, modern matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#E5E7EB",
        "axes.labelcolor": COLORS["text"],
        "text.color": COLORS["text"],
        "xtick.color": COLORS["neutral"],
        "ytick.color": COLORS["neutral"],
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.color": "#E5E7EB",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "figure.dpi": 120,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })


def format_number(n):
    """Format large numbers for display (1.2K, 3.4M, etc.)."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def create_kpi_card_figure(kpis):
    """
    Create a plotly figure with KPI cards.
    kpis: list of dicts with 'label', 'value', 'delta' (optional)
    """
    fig = go.Figure()
    n = len(kpis)
    for i, kpi in enumerate(kpis):
        fig.add_trace(go.Indicator(
            mode="number+delta" if "delta" in kpi else "number",
            value=kpi["value"],
            delta=kpi.get("delta"),
            title={"text": kpi["label"], "font": {"size": 14}},
            number={"font": {"size": 28}},
            domain={"x": [i/n, (i+1)/n], "y": [0, 1]},
        ))
    fig.update_layout(
        height=120,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
    )
    return fig
