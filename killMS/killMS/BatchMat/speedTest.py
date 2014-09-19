import timeit

def setup(N, M):
    return """
import numpy
from smallMatrixTools import mul, slowinv, invmul, sortedeig, inv
N = %i
M = %i
A = numpy.random.random((N, M, M))
B = numpy.random.random((N, M, M))
    """ % (N, M)

N = 10000
for M in (2, 3, 4, 5):
    s = setup(N, M)
    #slowinvmul = timeit.Timer("mul(slowinv(A), B)", setup=s).timeit(10)
    slowinvmul = timeit.Timer("slowinv(A)", setup=s).timeit(10)
    #fastinvmul = timeit.Timer("invmul(A, B)", setup=s).timeit(10)
    fastinvmul = timeit.Timer("inv(A)", setup=s).timeit(10)
    # fasteig = timeit.Timer("sortedeig(A, slow=False)", setup=s).timeit(10)
    # sloweig = timeit.Timer("sortedeig(A, slow=True)", setup=s).timeit(10)
    print ''
    print 'N, M, M: %i, %i, %i' % (N,M,M)
    #print 'mulinv speed up: %0.1f, eigvec speed up: %0.1f' % (slowinvmul / fastinvmul, sloweig / fasteig)
    print 'mulinv speed up: %0.1f' % (slowinvmul / fastinvmul)

## import pstats, cProfile

## import numpy
## from smallMatrixTools import invmul
## A = numpy.random.random((100000, 3, 3))
## B = numpy.random.random((100000, 3, 3))


## cProfile.runctx("invmul(A, B)", globals(), locals(), "Profile.prof")
## s = pstats.Stats("Profile.prof")
## s.strip_dirs().sort_stats("time").print_stats()

