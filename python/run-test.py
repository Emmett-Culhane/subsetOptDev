from subsum_cvxpy import *
from matplotlib import pyplot as plt

entry_bound = 100
nlevs       = 10

results = []
for nrows in range(5, 100):
    print 'nrows : %d | nlevs : %d | entry_bound : %d' % (nrows, nlevs, entry_bound)
    tmp = evalSubSum(**{
        "nrows"       : nrows,
        "nlevs"       : nlevs,
        "entry_bound" : entry_bound
    })
    results.append(tmp)

plt.plot([r['time'] for r in results])
plt.show()