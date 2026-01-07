# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_common import COLORS, setup_theme, apply_smoothing, style_axes, add_title

df = pd.read_json(sys.argv[1], orient="index")
df.index = pd.to_datetime(df.index, utc=True)

Path("individual-size-results").mkdir(exist_ok=True)

# Set up modern theme
setup_theme()

# Use color from common module
size_color = COLORS["default"]

for name, series in df["sizes"].apply(pd.Series).items():
    # Filter out None values which indicate missing data for 'name'
    sizes = series.dropna()

    if not sizes.empty:
        print(name)
        print(sizes)

        # Create figure with better proportions and higher DPI
        fig, ax = plt.subplots(figsize=(18, 9), dpi=100)

        # Prepare data for Seaborn
        plot_data = pd.DataFrame(
            {"date": sizes.index, "size": pd.to_numeric(sizes.values, errors="coerce")}
        )

        # Apply smoothing using rolling average
        plot_data["size_smooth"] = apply_smoothing(plot_data, None, "size")

        # Add gradient-like area fill first
        ax.fill_between(
            plot_data["date"],
            0,
            plot_data["size"],
            alpha=0.2,
            color=size_color,
            zorder=1,
            linewidth=0,
        )

        # Use Seaborn's lineplot with enhanced styling and smoothed data
        sns.lineplot(
            data=plot_data,
            x="date",
            y="size_smooth",
            color=size_color,
            linewidth=4,
            ax=ax,
            marker=False,  # Disable markers for smoother look
            alpha=1,
            zorder=3,
        )

        # Add title and subtitle
        add_title(
            ax,
            f'uutils coreutils — "{name}" Binary Size',
            "Individual utility size tracking over development history",
        )

        # Style axes with labels and grid
        style_axes(ax, xlabel="Date", ylabel="Size (kilobytes)")

        # Tight layout
        plt.tight_layout()

        # Save with high quality
        plt.savefig(
            f"individual-size-results/{name}.svg",
            format="svg",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
            metadata={
                "Creator": "uutils coreutils tracking",
                "Title": f"{name} Binary Size",
            },
        )
        plt.close(fig)
    else:
        print(f"Warning: No data found for '{name}'")
