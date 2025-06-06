# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)

df.columns.names = ["date"]

df.index = pd.to_datetime(df.index, utc=True, format="mixed")

print(df)

fig, ax = plt.subplots(figsize=(9.6, 7.2))
df.plot(y="size", color="gray", ax=ax, dashes=(2, 1), label="Size: multiple binaries (kilobytes)")
df.plot(y="multisize", color="green", ax=ax, dashes=(4, 1), label="Size: multicall binary (kilobytes)")
plt.title("Size evolution of Rust/Coreutils")
fig.autofmt_xdate()
plt.margins(0.01)
plt.savefig("size-results.svg", format="svg", dpi=199, bbox_inches="tight")
