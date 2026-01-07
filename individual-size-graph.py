# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.read_json(sys.argv[1], orient="index")
df.index = pd.to_datetime(df.index, utc=True)

Path("individual-size-results").mkdir(exist_ok=True)

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

# Modern color for size evolution
size_color = '#10B981'  # Modern green (Tailwind emerald)

for name, series in df["sizes"].apply(pd.Series).items():
    # Filter out None values which indicate missing data for 'name'
    sizes = series.dropna()

    if not sizes.empty:
        print(name)
        print(sizes)

        # Create figure with better proportions and higher DPI
        fig, ax = plt.subplots(figsize=(18, 9), dpi=100)

        # Prepare data for Seaborn
        plot_data = pd.DataFrame({
            'date': sizes.index,
            'size': pd.to_numeric(sizes['size'], errors='coerce')
        })

        # Apply smoothing using rolling average
        plot_data['size_smooth'] = plot_data['size'].rolling(window=15, min_periods=1, center=True).mean()

        # Add gradient-like area fill first
        ax.fill_between(plot_data['date'], 0, plot_data['size'],
                       alpha=0.2, color=size_color, zorder=1, linewidth=0)

        # Use Seaborn's lineplot with enhanced styling and smoothed data
        sns.lineplot(
            data=plot_data,
            x='date',
            y='size_smooth',
            color=size_color,
            linewidth=4,
            ax=ax,
            marker=False,  # Disable markers for smoother look
            alpha=1,
            zorder=3
        )

        # Modern title
        ax.text(0.5, 1.12, f'uutils coreutils — "{name}" Binary Size',
                ha='center', va='bottom', transform=ax.transAxes,
                fontsize=26, fontweight='bold', family='sans-serif', color='#1a1a1a')
        ax.text(0.5, 1.06, f'Individual utility size tracking over development history',
                ha='center', va='bottom', transform=ax.transAxes,
                fontsize=13, color='#6B7280', style='italic', alpha=0.9)

        ax.set_xlabel('Date', fontsize=15, fontweight='600', labelpad=15, color='#374151')
        ax.set_ylabel('Size (kilobytes)', fontsize=15, fontweight='600', labelpad=15, color='#374151')

        # Modern grid styling
        ax.grid(True, alpha=0.35, linestyle='-', linewidth=1, color='#E5E7EB', which='major', zorder=0)
        ax.grid(True, alpha=0.15, linestyle=':', linewidth=0.5, color='#F3F4F6', which='minor', zorder=0)
        ax.set_axisbelow(True)
        ax.minorticks_on()

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
        plt.savefig(f"individual-size-results/{name}.svg", format="svg", dpi=300,
                    bbox_inches="tight", facecolor='white', edgecolor='none',
                    metadata={'Creator': 'uutils coreutils tracking', 'Title': f'{name} Binary Size'})
        plt.close(fig)
    else:
        print(f"Warning: No data found for '{name}'")
