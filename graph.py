from datetime import datetime
from email.utils import parsedate

import sys
import time

import matplotlib.pyplot as plt
import pandas as pd

if len(sys.argv) <= 1:
   print('graph.py: Need an arg')
   sys.exit()

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
df.plot(y="total", color="blue", ax=ax)
df.plot(y="fail", color="gray", ax=ax, dashes=(2, 1))
df.plot(y="pass", color="green", ax=ax, dashes=(4, 1))
df.plot(y="error", color="orange", ax=ax, dashes=(6, 2))
df.plot(y="skip", color="violet", ax=ax, dashes=(8, 3))
plt.title("Rust/Coreutils running GNU's testsuite")
plt.xticks(rotation=45)
plt.savefig("gnu-results.png", dpi=199)
