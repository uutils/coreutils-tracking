# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import (COLORS, setup_theme, apply_smoothing, style_axes,
                          add_title, style_legend, add_reference_lines)

if len(sys.argv) <= 2:
   print("graph.py: <json file> <title>")
   sys.exit()

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)
title = sys.argv[2]

df.columns.names = ["date"]
df.index = pd.to_datetime(df.index, utc=True)

print(df)

# Set up modern theme
setup_theme()

# Create figure with better proportions and higher DPI
fig, ax = plt.subplots(figsize=(18, 9), dpi=100)

# Prepare data for plotting - melt to long format for Seaborn
plot_columns = ['total', 'pass', 'fail']
if "error" in df.columns and df['error'].notna().any():
    plot_columns.append('error')
plot_columns.append('skip')

df_plot = df[plot_columns].copy()
df_plot = df_plot.reset_index()
df_plot.rename(columns={df_plot.columns[0]: 'date'}, inplace=True)
df_plot_long = df_plot.melt(id_vars='date', var_name='metric', value_name='count')

# Convert string values to numeric
df_plot_long['count'] = pd.to_numeric(df_plot_long['count'], errors='coerce')

# Apply smoothing using rolling average (window of 15 for smoother lines)
df_plot_long['count_smooth'] = apply_smoothing(df_plot_long, 'metric', 'count')

# Use color palette from common module
palette = {k: COLORS[k] for k in ['total', 'pass', 'fail', 'error', 'skip']}

# Add gradient-like area fills first (behind lines)
for metric in ['total', 'pass', 'fail']:
    if metric in df_plot.columns:
        ax.fill_between(df_plot['date'], 0, df_plot[metric],
                       alpha=0.18, color=palette[metric], zorder=1, linewidth=0)

# Use Seaborn's lineplot with enhanced styling and smoothed data
sns.lineplot(
    data=df_plot_long,
    x='date',
    y='count_smooth',
    hue='metric',
    palette=palette,
    linewidth=3.5,
    ax=ax,
    markers=False,  # Disable markers for smoother look
    dashes=False,
    alpha=1,
    zorder=3
)

# Add title and subtitle
add_title(ax, f'uutils coreutils — {title} Test Suite Results',
          'Tracking test results over time to measure progress and compatibility')

# Style axes with labels and grid
style_axes(ax, xlabel='Date', ylabel='Number of Tests')

# Add reference lines
y_max = df_plot_long['count_smooth'].max()
add_reference_lines(ax, y_max)

# Style legend
handles, labels = ax.get_legend_handles_labels()
labels = [label.capitalize() for label in labels]
style_legend(ax, handles, labels, ncol=len(plot_columns), loc='upper left')

# Tight layout
plt.tight_layout()

# Save with high quality and optimized settings
plt.savefig(f"{title.lower()}-results.svg", format="svg", dpi=300,
            bbox_inches="tight", facecolor='white', edgecolor='none',
            metadata={'Creator': 'uutils coreutils tracking', 'Title': f'{title} Test Suite Results'})
