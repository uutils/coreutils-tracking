# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import (COLORS, setup_theme, apply_smoothing, style_axes,
                          add_title, style_legend)

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)

df.columns.names = ["date"]
df.index = pd.to_datetime(df.index, utc=True, format="mixed")

print(df)

# Set up modern theme
setup_theme()

# Create figure with better proportions and higher DPI
fig, ax = plt.subplots(figsize=(18, 9), dpi=100)

# Prepare data for Seaborn - melt to long format
df_plot = df[['size', 'multisize']].copy()
df_plot = df_plot.reset_index()
df_plot.columns = ['date', 'size', 'multisize']
df_plot_long = df_plot.melt(id_vars='date', var_name='binary_type', value_name='size_kb')

# Convert to numeric
df_plot_long['size_kb'] = pd.to_numeric(df_plot_long['size_kb'], errors='coerce')

# Apply smoothing using rolling average
df_plot_long['size_kb_smooth'] = apply_smoothing(df_plot_long, 'binary_type', 'size_kb')

# Use color palette from common module
palette = {
    'size': COLORS['size'],
    'multisize': COLORS['multisize']
}

# Add gradient-like area fills first
for col, color in palette.items():
    if col in df_plot.columns:
        ax.fill_between(df_plot['date'], 0, df_plot[col],
                       alpha=0.2, color=color, zorder=1, linewidth=0)

# Use Seaborn's lineplot with enhanced styling and smoothed data
sns.lineplot(
    data=df_plot_long,
    x='date',
    y='size_kb_smooth',
    hue='binary_type',
    palette=palette,
    linewidth=4,
    ax=ax,
    markers=False,  # Disable markers for smoother look
    dashes=False,
    alpha=1,
    zorder=3
)

# Add title and subtitle
add_title(ax, 'uutils coreutils — Binary Size Evolution',
          'Tracking binary size optimization and comparing build strategies')

# Style axes with labels and grid
style_axes(ax, xlabel='Date', ylabel='Size (kilobytes)')

# Style legend
handles, labels = ax.get_legend_handles_labels()
label_map = {
    'size': 'Multiple Binaries',
    'multisize': 'Multicall Binary (Optimized)'
}
labels = [label_map.get(label, label) for label in labels]
style_legend(ax, handles, labels, ncol=1, loc='upper left')

# Tight layout
plt.tight_layout()

# Save with high quality
plt.savefig("size-results.svg", format="svg", dpi=300,
            bbox_inches="tight", facecolor='white', edgecolor='none',
            metadata={'Creator': 'uutils coreutils tracking', 'Title': 'Binary Size Evolution'})
