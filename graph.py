import matplotlib.pyplot as plt
import pandas as pd
d = pd.read_json("gnu-result.json")
df = pd.DataFrame(d)
df = df.transpose()
print (df)

ax = plt.gca()
df.plot(y='total',color='blue',ax=ax)
df.plot(y='fail',color='red',ax=ax)
df.plot(y='pass',color='green',ax=ax)

plt.savefig('output.png')


