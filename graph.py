import matplotlib.pyplot as plt
import pandas as pd
import sys

d = pd.read_json(sys.argv[1])
df = pd.DataFrame(d)
df = df.transpose()
print(df)

ax = plt.gca()
df.plot(y="total", color="blue", ax=ax)
df.plot(y="fail", color="red", ax=ax)
df.plot(y="pass", color="green", ax=ax)

plt.xticks(rotation=45)
plt.savefig("gnu-results.png", dpi=259)
