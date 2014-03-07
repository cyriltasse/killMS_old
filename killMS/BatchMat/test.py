import numpy as np
from smallMatrixTools import mul, slowinv, invmul, mulinv, sortedeig

np.random.seed(1)
N = 5
for M in (2, 3, 4, 5):

    A = -np.random.random((N, M, M))
    for i in range(M):
        A[i, i] += 1 + M
    B = np.random.random((N, M, M))
    I = np.identity(A.shape[-1])
    print np.allclose(mulinv(A, A), I[np.newaxis])

    print np.allclose(invmul(A, A), I[np.newaxis])

    e, R = sortedeig(A)
    eslow, Rslow = sortedeig(A, slow=True)
    print np.allclose(e, eslow)
    print np.allclose(mul(A, R), e[:,np.newaxis] * R)
    
    E = e[:,:,np.newaxis] * I
    
    print np.allclose(A, mulinv(mul(R, E), R))
    raw_input('M: ' + str(M))


