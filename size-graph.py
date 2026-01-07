# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)

df.columns.names = ["date"]
df.index = pd.to_datetime(df.index, utc=True, format="mixed")

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

# Prepare data for Seaborn - melt to long format
df_plot = df[['size', 'multisize']].copy()
df_plot = df_plot.reset_index()
df_plot.columns = ['date', 'size', 'multisize']
df_plot_long = df_plot.melt(id_vars='date', var_name='binary_type', value_name='size_kb')

# Convert to numeric
df_plot_long['size_kb'] = pd.to_numeric(df_plot_long['size_kb'], errors='coerce')

# Apply smoothing using rolling average
df_plot_long['size_kb_smooth'] = df_plot_long.groupby('binary_type')['size_kb'].transform(
    lambda x: x.rolling(window=15, min_periods=1, center=True).mean()
)

# Modern color palette
palette = {
    'size': '#6366F1',         # Modern indigo
    'multisize': '#10B981'     # Modern green (Tailwind emerald)
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

# Modern title
ax.text(0.5, 1.12, 'uutils coreutils — Binary Size Evolution',
        ha='center', va='bottom', transform=ax.transAxes,
        fontsize=26, fontweight='bold', family='sans-serif', color='#1a1a1a')
ax.text(0.5, 1.06, 'Tracking binary size optimization and comparing build strategies',
        ha='center', va='bottom', transform=ax.transAxes,
        fontsize=13, color='#6B7280', style='italic', alpha=0.9)

ax.set_xlabel('Date', fontsize=15, fontweight='600', labelpad=15, color='#374151')
ax.set_ylabel('Size (kilobytes)', fontsize=15, fontweight='600', labelpad=15, color='#374151')

# Modern grid styling
ax.grid(True, alpha=0.35, linestyle='-', linewidth=1, color='#E5E7EB', which='major', zorder=0)
ax.grid(True, alpha=0.15, linestyle=':', linewidth=0.5, color='#F3F4F6', which='minor', zorder=0)
ax.set_axisbelow(True)
ax.minorticks_on()

# Modern legend
handles, labels = ax.get_legend_handles_labels()
label_map = {
    'size': 'Multiple Binaries',
    'multisize': 'Multicall Binary (Optimized)'
}
labels = [label_map.get(label, label) for label in labels]
legend = ax.legend(handles, labels, loc='upper left', frameon=True,
                   fancybox=False, shadow=False, fontsize=13,
                   bbox_to_anchor=(0, 1.04),
                   edgecolor='#D1D5DB', framealpha=0.98,
                   borderpad=1.2, labelspacing=0.8)
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

# Modern background
ax.patch.set_facecolor('#FAFAFA')
ax.patch.set_alpha(0.6)

# Add subtle shadow effect
ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor='none', edgecolor='#E5E7EB',
                           linewidth=3, zorder=-1))

# Tight layout
plt.tight_layout()

# Save with high quality
plt.savefig("size-results.svg", format="svg", dpi=300,
            bbox_inches="tight", facecolor='white', edgecolor='none',
            metadata={'Creator': 'uutils coreutils tracking', 'Title': 'Binary Size Evolution'})
