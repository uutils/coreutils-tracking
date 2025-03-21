# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_json(sys.argv[1], orient="index")

Path("individual-size-results").mkdir(exist_ok=True)


df = pd.read_json(sys.argv[1], orient="index")

Path("individual-size-results").mkdir(exist_ok=True)

for name in df.sizes.values[0].keys():
    # Check if the name exists in each dictionary
    sizes = df.sizes.map(lambda v: v.get(name))

    # Filter out None values which indicate missing data for 'name'
    sizes = sizes[sizes.notnull()]

    if not sizes.empty:
        print(name)
        print(sizes)
        sizes.plot(y="size", color="green")
        plt.title(f'Size evolution of "{name}" binary (kilobytes)')
        plt.xticks(rotation=45)
        plt.savefig(f"individual-size-results/{name}.png", dpi=199)
        plt.clf()
    else:
        print(f"Warning: No data found for '{name}'")
