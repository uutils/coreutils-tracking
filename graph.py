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
df.plot(y="total", color="blue", ax=ax)
df.plot(y="fail", color="red", ax=ax)
df.plot(y="pass", color="green", ax=ax)
df.plot(y="error", color="orange", ax=ax)
plt.title("Rust/Coreutils running GNU's testsuite")
plt.xticks(rotation=45)
plt.savefig("gnu-results.png", dpi=199)
