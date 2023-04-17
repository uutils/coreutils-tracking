import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_json(sys.argv[1], orient="index")

Path("individual-size-results").mkdir(exist_ok=True)

for name, _ in df.sizes.values[0].items():
    print(name)
    sizes = df.sizes.map(lambda v: v[name])
    print(sizes)
    sizes.plot(y="size", color="green")
    plt.title(f'Size evolution of "{name}" binary (byte)')
    plt.xticks(rotation=45)
    plt.savefig(f"individual-size-results/{name}.png", dpi=199)
    plt.clf()
