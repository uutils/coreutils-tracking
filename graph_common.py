# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Common styling and utilities for graph generation."""

import matplotlib.pyplot as plt
import seaborn as sns


# Modern vibrant color palette
COLORS = {
    "total": "#0066CC",  # Vibrant blue
    "pass": "#10B981",  # Modern green (Tailwind emerald)
    "fail": "#EF4444",  # Modern red (Tailwind red)
    "error": "#F59E0B",  # Modern amber
    "skip": "#8B5CF6",  # Modern purple (Tailwind violet)
    "size": "#6366F1",  # Modern indigo
    "multisize": "#10B981",  # Modern green (Tailwind emerald)
    "default": "#10B981",  # Modern green (Tailwind emerald)
}


def setup_theme():
    """Set up modern Seaborn theme with enhanced settings."""
    sns.set_theme(style="ticks", context="talk", palette="muted")
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Inter",
                "SF Pro Display",
                "Segoe UI",
                "DejaVu Sans",
                "Arial",
            ],
            "axes.facecolor": "#FAFAFA",
            "figure.facecolor": "white",
            "axes.edgecolor": "#CCCCCC",
            "axes.linewidth": 0.8,
            "xtick.color": "#555555",
            "ytick.color": "#555555",
        }
    )


def apply_smoothing(df, group_col, value_col, window=15):
    """Apply rolling average smoothing to data.

    Args:
        df: DataFrame with data to smooth
        group_col: Column name to group by (or None for no grouping)
        value_col: Column name containing values to smooth
        window: Rolling window size (default: 15)

    Returns:
        Series with smoothed values
    """
    if group_col:
        return df.groupby(group_col)[value_col].transform(
            lambda x: x.rolling(window=window, min_periods=1, center=True).mean()
        )
    else:
        return df[value_col].rolling(window=window, min_periods=1, center=True).mean()


def style_axes(ax, xlabel="Date", ylabel="Value"):
    """Apply modern styling to axes.

    Args:
        ax: Matplotlib axes object
        xlabel: Label for x-axis
        ylabel: Label for y-axis
    """
    ax.set_xlabel(xlabel, fontsize=15, fontweight="600", labelpad=15, color="#374151")
    ax.set_ylabel(ylabel, fontsize=15, fontweight="600", labelpad=15, color="#374151")

    # Modern grid styling
    ax.grid(
        True,
        alpha=0.35,
        linestyle="-",
        linewidth=1,
        color="#E5E7EB",
        which="major",
        zorder=0,
    )
    ax.grid(
        True,
        alpha=0.15,
        linestyle=":",
        linewidth=0.5,
        color="#F3F4F6",
        which="minor",
        zorder=0,
    )
    ax.set_axisbelow(True)
    ax.minorticks_on()

    # Format x-axis dates
    plt.xticks(rotation=45, ha="right")
    ax.margins(x=0.01)
    ax.set_ylim(bottom=0)

    # Modern spine styling
    sns.despine(ax=ax, top=True, right=True, left=False, bottom=False, offset=8)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_linewidth(2)
    ax.spines["left"].set_color("#9CA3AF")
    ax.spines["bottom"].set_color("#9CA3AF")

    # Modern background
    ax.patch.set_facecolor("#FAFAFA")
    ax.patch.set_alpha(0.6)

    # Add subtle shadow effect
    ax.add_patch(
        plt.Rectangle(
            (0, 0),
            1,
            1,
            transform=ax.transAxes,
            facecolor="none",
            edgecolor="#E5E7EB",
            linewidth=3,
            zorder=-1,
        )
    )


def add_title(ax, title, subtitle=None):
    """Add modern title and optional subtitle to axes.

    Args:
        ax: Matplotlib axes object
        title: Main title text
        subtitle: Optional subtitle text
    """
    ax.text(
        0.5,
        1.12,
        title,
        ha="center",
        va="bottom",
        transform=ax.transAxes,
        fontsize=26,
        fontweight="bold",
        family="sans-serif",
        color="#1a1a1a",
    )

    if subtitle:
        ax.text(
            0.5,
            1.06,
            subtitle,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            fontsize=13,
            color="#6B7280",
            style="italic",
            alpha=0.9,
        )


def style_legend(ax, handles, labels, ncol=1, loc="upper left"):
    """Apply modern styling to legend.

    Args:
        ax: Matplotlib axes object
        handles: Legend handles
        labels: Legend labels
        ncol: Number of columns (default: 1)
        loc: Legend location (default: 'upper left')

    Returns:
        Legend object
    """
    legend = ax.legend(
        handles,
        labels,
        loc=loc,
        frameon=True,
        fancybox=False,
        shadow=False,
        ncol=ncol,
        bbox_to_anchor=(0, 1.04) if "left" in loc else (1, 1.04),
        fontsize=13,
        edgecolor="#D1D5DB",
        framealpha=0.98,
        borderpad=1.2,
        labelspacing=0.8,
        columnspacing=2,
    )
    legend.get_frame().set_facecolor("#FFFFFF")
    legend.get_frame().set_linewidth(2)
    legend.get_frame().set_boxstyle("round,pad=0.5")
    return legend


GNU_COREUTILS_RELEASES = [
    ("9.0", "2021-09-24"),
    ("9.1", "2022-04-15"),
    ("9.2", "2023-03-20"),
    ("9.3", "2023-04-18"),
    ("9.4", "2023-08-29"),
    ("9.5", "2024-03-28"),
    ("9.6", "2025-01-17"),
    ("9.7", "2025-04-09"),
    ("9.8", "2025-09-22"),
    ("9.9", "2025-11-10"),
    ("9.10", "2026-02-04"),
    ("9.11", "2026-04-23"),
]


def add_gnu_release_markers(ax, x_min, x_max, y_max, releases=GNU_COREUTILS_RELEASES):
    """Draw vertical bars at GNU coreutils release dates within the data range."""
    import pandas as pd

    x_min = pd.to_datetime(x_min, utc=True)
    x_max = pd.to_datetime(x_max, utc=True)
    for version, date_str in releases:
        rel_date = pd.to_datetime(date_str, utc=True)
        if x_min <= rel_date <= x_max:
            ax.axvline(
                x=rel_date,
                color="#6B7280",
                linestyle="--",
                linewidth=1.2,
                alpha=0.6,
                zorder=2,
            )
            ax.text(
                rel_date,
                y_max * 0.02,
                f"v{version}",
                rotation=90,
                fontsize=10,
                color="#374151",
                ha="right",
                va="bottom",
                alpha=0.85,
                zorder=4,
            )


def add_reference_lines(ax, y_max):
    """Add horizontal reference lines at key values.

    Args:
        ax: Matplotlib axes object
        y_max: Maximum y value for calculating reference positions
    """
    if y_max > 100:
        ax.axhline(
            y=y_max * 0.75,
            color="#D1D5DB",
            linestyle="--",
            linewidth=0.8,
            alpha=0.3,
            zorder=0,
        )
        ax.axhline(
            y=y_max * 0.5,
            color="#D1D5DB",
            linestyle="--",
            linewidth=0.8,
            alpha=0.3,
            zorder=0,
        )
