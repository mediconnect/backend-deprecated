import numpy as np
from scipy.stats import hypergeom

a = np.array([1, 3, 10])
b = np.array([5, 3, 4])

left = a.astype(bool)
right = b.astype(bool)
k = np.count_nonzero(np.bitwise_and(left, right))
prb = hypergeom.cdf(k, len(left), np.count_nonzero(left), np.count_nonzero(right))
print 1 - prb