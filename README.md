atmospy
=======

Python library for the atmospheric sciences

p = '/Users/dh/Documents/GitHub/quals/quals/data/Tata/March 2016'

import atmospy
import atmospy.io

df = atmospy.AlphasenseLoader()
df.load(p, "X102 PM*.csv")

a = atmospy.AlphasenseOPCN2(dN = df.hist.resample('10min').mean())
