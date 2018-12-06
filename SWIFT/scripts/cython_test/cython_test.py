"""

Test cython
http://nealhughes.net/cython1/

"""

import time
from math import exp
import numpy as np


def timeit(func):
    def f(*args, **kwargs):
        args = list(args)
        start_time = time.time()
        rv = func(*args, **kwargs)
        end_time = time.time()
        print("Execution time = {0:.0f} sec".format(end_time-start_time))
        return rv
    return f


@timeit
def rbf_network(X, beta, theta):

    N = X.shape[0]
    D = X.shape[1]
    Y = np.zeros(N)

    for i in range(N):
        for j in range(N):
            r = 0
            for d in range(D):
                r += (X[j, d] - X[i, d]) ** 2
            r = r**0.5
            Y[i] += beta[j] * exp(-(r * theta)**2)

    return Y



if __name__ == '__main__':
    D = 5
    N = 1000
    X = np.array([np.random.rand(N) for d in range(D)]).T
    beta = np.random.rand(N)
    theta = 10
    rbf_network(X, beta, theta)