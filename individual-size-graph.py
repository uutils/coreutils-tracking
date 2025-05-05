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


for name in df.sizes.values[0]:
    # Check if the name exists in each dictionary
    sizes = df.sizes.map(lambda v: v.get(name))

    # Filter out None values which indicate missing data for 'name'
    sizes = sizes[sizes.notnull()]

    if not sizes.empty:
        print(name)
        print(sizes)
        fig, _ax = plt.subplots(figsize=(9.6, 7.2))
        sizes.plot(y="size", color="green")
        plt.title(f'Size evolution of "{name}" binary (kilobytes)')
        fig.autofmt_xdate()
        plt.margins(0.01)
        plt.savefig(f"individual-size-results/{name}.svg", format="svg", dpi=199, bbox_inches="tight")
        plt.clf()
    else:
        print(f"Warning: No data found for '{name}'")
