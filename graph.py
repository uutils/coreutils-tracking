# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

if len(sys.argv) <= 2:
   print("graph.py: <json file> <title>")
   sys.exit()

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)
title = sys.argv[2]

df.columns.names = ["date"]
df.index = pd.to_datetime(df.index, utc=True)

print(df)

# Set modern Seaborn style with enhanced settings
sns.set_theme(style="ticks", context="talk", palette="muted")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'SF Pro Display', 'Segoe UI', 'Arial'],
    'axes.facecolor': '#FAFAFA',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#CCCCCC',
    'axes.linewidth': 0.8,
    'xtick.color': '#555555',
    'ytick.color': '#555555',
})

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
df_plot_long['count_smooth'] = df_plot_long.groupby('metric')['count'].transform(
    lambda x: x.rolling(window=15, min_periods=1, center=True).mean()
)

# Modern vibrant color palette
palette = {
    'total': '#0066CC',    # Vibrant blue
    'pass': '#10B981',     # Modern green (Tailwind emerald)
    'fail': '#EF4444',     # Modern red (Tailwind red)
    'error': '#F59E0B',    # Modern amber
    'skip': '#8B5CF6'      # Modern purple (Tailwind violet)
}

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

# Modern title with better spacing
ax.text(0.5, 1.12, f'uutils coreutils — {title} Test Suite Results',
        ha='center', va='bottom', transform=ax.transAxes,
        fontsize=26, fontweight='bold', family='sans-serif', color='#1a1a1a')
ax.text(0.5, 1.06, 'Tracking test results over time to measure progress and compatibility',
        ha='center', va='bottom', transform=ax.transAxes,
        fontsize=13, color='#6B7280', style='italic', alpha=0.9)

ax.set_xlabel('Date', fontsize=15, fontweight='600', labelpad=15, color='#374151')
ax.set_ylabel('Number of Tests', fontsize=15, fontweight='600', labelpad=15, color='#374151')

# Modern grid styling with better contrast
ax.grid(True, alpha=0.35, linestyle='-', linewidth=1, color='#E5E7EB', which='major', zorder=0)
ax.grid(True, alpha=0.15, linestyle=':', linewidth=0.5, color='#F3F4F6', which='minor', zorder=0)
ax.set_axisbelow(True)
ax.minorticks_on()

# Add subtle horizontal reference lines at key values
y_max = df_plot_long['count_smooth'].max()
if y_max > 100:
    ax.axhline(y=y_max * 0.75, color='#D1D5DB', linestyle='--', linewidth=0.8, alpha=0.3, zorder=0)
    ax.axhline(y=y_max * 0.5, color='#D1D5DB', linestyle='--', linewidth=0.8, alpha=0.3, zorder=0)

# Modern legend styling
handles, labels = ax.get_legend_handles_labels()
# Capitalize labels
labels = [label.capitalize() for label in labels]
legend = ax.legend(handles, labels, loc='upper left', frameon=True,
                   fancybox=False, shadow=False, ncol=len(plot_columns),
                   bbox_to_anchor=(0, 1.04), fontsize=13,
                   edgecolor='#D1D5DB', framealpha=0.98,
                   borderpad=1.2, labelspacing=0.8, columnspacing=2)
legend.get_frame().set_facecolor('#FFFFFF')
legend.get_frame().set_linewidth(2)
legend.get_frame().set_boxstyle('round,pad=0.5')

# Format x-axis dates
plt.xticks(rotation=45, ha='right')
ax.margins(x=0.01)
ax.set_ylim(bottom=0)

# Modern spine styling
sns.despine(ax=ax, top=True, right=True, left=False, bottom=False, offset=8)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_color('#9CA3AF')
ax.spines['bottom'].set_color('#9CA3AF')

# Modern gradient-like background
ax.patch.set_facecolor('#FAFAFA')
ax.patch.set_alpha(0.6)

# Add a subtle shadow effect
ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor='none', edgecolor='#E5E7EB',
                           linewidth=3, zorder=-1))

# Tight layout
plt.tight_layout()

# Save with high quality and optimized settings
plt.savefig(f"{title.lower()}-results.svg", format="svg", dpi=300,
            bbox_inches="tight", facecolor='white', edgecolor='none',
            metadata={'Creator': 'uutils coreutils tracking', 'Title': f'{title} Test Suite Results'})
