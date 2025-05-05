# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

import sys

import matplotlib.pyplot as plt
import pandas as pd

if len(sys.argv) <= 2:
   print("graph.py: <json file> <title>")
   sys.exit()

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)
title = sys.argv[2]

df.columns.names = ["date"]

df.index = pd.to_datetime(df.index, utc=True)

print(df)

fig, ax = plt.subplots(figsize=(9.6, 7.2))
df.plot(y="total", color="blue", ax=ax)
df.plot(y="fail", color="gray", ax=ax, dashes=(2, 1))
df.plot(y="pass", color="green", ax=ax, dashes=(4, 1))
if "error" in df:
   df.plot(y="error", color="orange", ax=ax, dashes=(6, 2))
df.plot(y="skip", color="violet", ax=ax, dashes=(8, 3))
plt.title(f"Rust/Coreutils running {title}'s testsuite")
fig.autofmt_xdate()
plt.margins(0.01)
plt.ylim(ymin=0)
plt.savefig(f"{title.lower()}-results.svg", format="svg", dpi=199, bbox_inches="tight")
