# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Render unsafe-result.json as an SVG, breaking the total down by category."""

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import (
    setup_theme,
    apply_smoothing,
    style_axes,
    add_title,
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

fig, ax = plt.subplots(figsize=(18, 9), dpi=100)

# Color palette tuned for the unsafe categories. `total` is the heavyweight
# blue line; the per-category lines sit underneath.
palette = {
    "total": "#0066CC",
    "blocks": "#10B981",
    "fn": "#EF4444",
    "extern": "#F59E0B",
    "attr": "#8B5CF6",
    "impl": "#EC4899",
    "trait": "#14B8A6",
}

# Keep only the categories that actually have non-zero values to avoid a
# legend cluttered with flat-zero lines (impl/trait have been zero for years).
categories = ["total", "blocks", "fn", "extern", "attr", "impl", "trait"]
present = []
for col in categories:
    if col not in df.columns:
        continue
    vals = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if col == "total" or vals.max() > 0:
        present.append(col)

df_plot = df[present].copy().reset_index()
df_plot.rename(columns={df_plot.columns[0]: "date"}, inplace=True)
df_long = df_plot.melt(id_vars="date", var_name="category", value_name="count")
df_long["count"] = pd.to_numeric(df_long["count"], errors="coerce")
df_long["count_smooth"] = apply_smoothing(df_long, "category", "count")

sns.lineplot(
    data=df_long,
    x="date",
    y="count_smooth",
    hue="category",
    palette={k: palette[k] for k in present},
    hue_order=present,
    linewidth=3.5,
    ax=ax,
    markers=False,
    dashes=False,
    alpha=1,
    zorder=3,
)

add_title(
    ax,
    "uutils coreutils — `unsafe` Usage Over Time",
    "Tracking unsafe blocks, fns, externs and attributes across the codebase",
)

style_axes(ax, xlabel="Date", ylabel="Count of `unsafe` lines")

label_map = {
    "total": "Total",
    "blocks": "unsafe { … }",
    "fn": "unsafe fn",
    "extern": "unsafe extern",
    "attr": "#[unsafe(…)]",
    "impl": "unsafe impl",
    "trait": "unsafe trait",
}
handles, labels = ax.get_legend_handles_labels()
labels = [label_map.get(label, label) for label in labels]
style_legend(ax, handles, labels, ncol=len(present), loc="upper left")

# Latest-snapshot box (mirrors the GNU graph).
latest = df.iloc[-1]
total_val = int(pd.to_numeric(latest["total"], errors="coerce") or 0)
parts = []
for col in ["blocks", "fn", "extern", "attr", "impl", "trait"]:
    if col in latest:
        n = int(pd.to_numeric(latest[col], errors="coerce") or 0)
        if n > 0:
            parts.append(f"{label_map[col]}: {n}")

textstr = f"Latest:\nTotal: {total_val}\n" + "\n".join(parts)
props = dict(
    boxstyle="round,pad=0.8",
    facecolor="#FFFFFF",
    edgecolor="#D1D5DB",
    linewidth=2,
    alpha=0.95,
)
ax.text(
    0.98,
    1.15,
    textstr,
    transform=ax.transAxes,
    fontsize=13,
    verticalalignment="top",
    horizontalalignment="right",
    bbox=props,
    color="#374151",
    fontweight="600",
    zorder=10,
)

plt.tight_layout()

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
