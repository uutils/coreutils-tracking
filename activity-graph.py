# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Render activity-result.json with three stacked panels comparing GNU and
uutils coreutils: commits per month, active contributors per month and
cumulative distinct contributors. All panels share an x-axis so trends line
up vertically.
"""

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import (
    add_gnu_release_markers,
    apply_smoothing,
    setup_theme,
    style_axes,
    style_legend,
)

if len(sys.argv) <= 1:
    print("activity-graph.py: <json file>")
    sys.exit()

raw = pd.read_json(sys.argv[1], orient="index", convert_dates=False)

# Flatten {"2021-01": {"gnu": {...}, "uutils": {...}}} into one row per
# (month, project).
rows = []
for month, projects in raw.iterrows():
    for project, values in projects.items():
        rows.append(
            {
                "date": pd.to_datetime(month, format="%Y-%m", utc=True),
                "project": project,
                **{k: int(v) for k, v in values.items()},
            }
        )

df = pd.DataFrame(rows).sort_values("date")

print(df)

setup_theme()

palette = {
    "gnu": "#0066CC",
    "uutils": "#10B981",
}

label_map = {
    "gnu": "GNU coreutils",
    "uutils": "uutils coreutils",
}


def plot_panel(ax, metric, ylabel, smooth=True):
    """Plot one metric for both projects on `ax`."""
    data = df[["date", "project", metric]].copy()
    if smooth:
        # 3-month rolling mean: monthly counts are spiky (release crunches,
        # hackathons) and the trend is what matters here.
        data["value"] = apply_smoothing(data, "project", metric, window=3)
    else:
        data["value"] = data[metric]

    sns.lineplot(
        data=data,
        x="date",
        y="value",
        hue="project",
        palette=palette,
        hue_order=["gnu", "uutils"],
        linewidth=3,
        ax=ax,
        markers=False,
        dashes=False,
        alpha=1,
        zorder=3,
    )
    style_axes(ax, xlabel="Date", ylabel=ylabel)

    y_max = data["value"].max()
    add_gnu_release_markers(ax, df["date"].min(), df["date"].max(), y_max)

    handles, labels = ax.get_legend_handles_labels()
    labels = [label_map.get(label, label) for label in labels]
    style_legend(ax, handles, labels, ncol=2, loc="upper left")


fig, (ax_top, ax_mid, ax_bot) = plt.subplots(
    3, 1, figsize=(18, 20), dpi=100, sharex=True
)

plot_panel(ax_top, "commits", "Commits / month")
plot_panel(ax_mid, "authors", "Active contributors / month")
plot_panel(ax_bot, "cumulative_authors", "Distinct contributors (since day 1)", False)

fig.suptitle(
    "GNU vs uutils coreutils — Development Activity Since 2021",
    fontsize=26,
    fontweight="bold",
    color="#1a1a1a",
    y=0.995,
)
fig.text(
    0.5,
    0.972,
    "Non-merge commits, bots excluded. Top two panels are 3-month rolling averages; "
    "the cumulative panel counts every contributor since each project's first commit.",
    ha="center",
    va="top",
    fontsize=13,
    color="#6B7280",
    style="italic",
    alpha=0.9,
)

# Hide the upper panels' x-tick labels — they duplicate the bottom panel's.
for ax in (ax_top, ax_mid):
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.set_xlabel("")

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(
    "activity-results.svg",
    format="svg",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
    metadata={
        "Creator": "uutils coreutils tracking",
        "Title": "Development Activity Evolution",
    },
)
