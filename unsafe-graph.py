# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Render unsafe-result.json with two stacked panels:
top — code vs test split, bottom — per-keyword type breakdown.
Both panels share an x-axis so trends line up vertically.
"""

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import (
    setup_theme,
    apply_smoothing,
    style_axes,
    style_legend,
)

if len(sys.argv) <= 1:
    print("unsafe-graph.py: <json file>")
    sys.exit()

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)
df.columns.names = ["date"]
df.index = pd.to_datetime(df.index, utc=True, format="mixed")
df = df.sort_index()

print(df)

setup_theme()

palette = {
    "total": "#0066CC",
    "code": "#10B981",
    "test": "#F59E0B",
    "blocks": "#6366F1",
    "extern": "#EF4444",
    "attr": "#8B5CF6",
    "fn": "#EC4899",
    "impl": "#14B8A6",
    "trait": "#A16207",
}

label_map = {
    "total": "Total",
    "code": "Code (src/, uucore/, …)",
    "test": "Tests (tests/, fuzz/)",
    "blocks": "unsafe { … }",
    "extern": "unsafe extern",
    "attr": "#[unsafe(…)]",
    "fn": "unsafe fn",
    "impl": "unsafe impl",
    "trait": "unsafe trait",
}


def plot_panel(ax, df, series, ylabel):
    """Plot total + the given series on `ax`, no area fills."""
    cols = ["total"] + series
    df_plot = df[cols].copy().reset_index()
    df_plot.rename(columns={df_plot.columns[0]: "date"}, inplace=True)
    for col in cols:
        df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce")

    df_long = df_plot.melt(id_vars="date", var_name="series", value_name="count")
    df_long["count_smooth"] = apply_smoothing(df_long, "series", "count")

    sns.lineplot(
        data=df_long,
        x="date",
        y="count_smooth",
        hue="series",
        palette={k: palette[k] for k in cols},
        hue_order=cols,
        linewidth=3,
        ax=ax,
        markers=False,
        dashes=False,
        alpha=1,
        zorder=3,
    )
    style_axes(ax, xlabel="Date", ylabel=ylabel)

    handles, labels = ax.get_legend_handles_labels()
    labels = [label_map.get(label, label) for label in labels]
    style_legend(ax, handles, labels, ncol=len(cols), loc="upper left")


# Drop type series that have stayed at 0 across the whole history.
all_types = ["blocks", "extern", "attr", "fn", "impl", "trait"]
type_series = [
    col
    for col in all_types
    if col in df.columns and pd.to_numeric(df[col], errors="coerce").fillna(0).max() > 0
]

fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(18, 14), dpi=100, sharex=True)

plot_panel(ax_top, df, ["code", "test"], "Code vs Tests")
plot_panel(ax_bot, df, type_series, "By keyword type")

# Shared title/subtitle above the top panel.
fig.suptitle(
    "uutils coreutils — `unsafe` Usage Over Time",
    fontsize=26,
    fontweight="bold",
    color="#1a1a1a",
    y=0.995,
)
fig.text(
    0.5,
    0.965,
    "Top: code vs tests/fuzz. Bottom: breakdown by `unsafe` keyword form.",
    ha="center",
    va="top",
    fontsize=13,
    color="#6B7280",
    style="italic",
    alpha=0.9,
)

# Hide the upper panel's x-tick labels — they duplicate the lower panel's.
plt.setp(ax_top.get_xticklabels(), visible=False)
ax_top.set_xlabel("")

plt.tight_layout(rect=[0, 0, 1, 0.94])

plt.savefig(
    "unsafe-results.svg",
    format="svg",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
    metadata={
        "Creator": "uutils coreutils tracking",
        "Title": "Unsafe Usage Evolution",
    },
)
