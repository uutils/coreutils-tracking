# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from datetime import datetime
from email.utils import parsedate

import sys
import time

import matplotlib.pyplot as plt
import pandas as pd

d = pd.read_json(sys.argv[1], orient="index")
df = pd.DataFrame(d)

df.columns.names = ["date"]

as_list = df.index.tolist()
for i in as_list:
    idx = as_list.index(i)
    t = parsedate(i)
    as_list[idx] = datetime.fromtimestamp(time.mktime(t))

df.index = as_list

print(df)

ax = plt.gca()
df.plot(y="size", color="gray", ax=ax, dashes=(2, 1), label="Size: multiple binaries (byte)")
df.plot(y="multisize", color="green", ax=ax, dashes=(4, 1), label="Size: multicall binary (byte)")
plt.title("Size evolution of Rust/Coreutils")
plt.xticks(rotation=45)
plt.savefig("size-results.png", dpi=199)
