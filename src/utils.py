"""
Shared utility functions for visualization and formatting.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plotly.express as px
import plotly.graph_objects as go


# Color palette — modern, professional, business-facing
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

TIER_ORDER = ["mid", "macro_low", "macro", "mega", "mega_plus"]
TIER_LABELS = {
    "mid": "12–15M",
    "macro_low": "15–30M",
    "macro": "30–60M",
    "mega": "60–100M",
    "mega_plus": "100M+",
}
TIER_COLORS = ["#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]

CATEGORY_COLORS = px.colors.qualitative.Set2


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
    """Format large numbers for display (1.2K, 3.4M, 5.6B, etc.)."""
    if n is None or (isinstance(n, float) and n != n):
        return "N/A"
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def format_currency(n):
    """Format currency values."""
    if n is None or (isinstance(n, float) and n != n):
        return "N/A"
    if abs(n) >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    elif abs(n) >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:,.0f}"
