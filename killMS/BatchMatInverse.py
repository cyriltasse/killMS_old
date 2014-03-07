import numpy as np
import ClassTimeIt
import BatchMatInverse_C
import numpy.linalg as linalg



def BatchInvert(A):                       
    for i in range(A.shape[0]):
        A[i][:,:]=linalg.inv(A[i][:,:])
    return A 
        
def BatchInvert2(A):                       
    A=np.array(map(np.linalg.inv, A)) 
    return A

def test(N=10000):
    A=(np.random.randn(N,2,2)+1j*np.random.randn(N,2,2)).astype(np.complex128)
    B=A.copy()
    B.fill(0)
    timer=ClassTimeIt.ClassTimeIt()
    B=BatchMatInverse_C.FastInv(A,B)
    timer.timeit()
    A=BatchInvert2(A)
    timer.timeit()
    print A-B

def testDot(S=(200,10000)):
    A=np.complex128(np.random.randn(S[0],S[1]))
    B=(A.T).copy()
    C1=np.complex128(np.zeros(S))
    C1.fill(0)

    timer=ClassTimeIt.ClassTimeIt()
    BatchMatInverse_C.FastDotAAT(A,A,C1)
    timer.timeit()

    C2=np.dot(A,B)
    timer.timeit()

    B=(B.T).copy()
    timer.reinit()
    C2=np.dot(A,B.T)
    timer.timeit()

def Kron():

    S=(2, 2, 2, 2, 2)
    na,nt,nf,np0,np1=S
    a=(np.random.randn(na,nt,nf,2,2).reshape((na*nt*nf,2,2))).astype(np.complex128)
    akeep=a.copy()

    Apinv=a.copy()
    Aqinv=a.copy()

    print "Shape %s"%str(a.shape)
    timer=ClassTimeIt.ClassTimeIt()
    BatchMatInverse_C.FastInv(a,Apinv,H=0)
    timer.timeit()
    BatchMatInverse_C.FastInv(a,Aqinv,H=1)
    timer.timeit()
    BatchMatInverse_C.FastProd22(Apinv,a,a)
    timer.timeit()
    BatchMatInverse_C.FastProd22(a,Aqinv,a)
    timer.timeit()
    aout0=(a.reshape((na,nt,nf,2,2))).copy()
    aout1=np.zeros_like(akeep)

    for i in range(na*nt*nf):
        Apinv[i]=np.linalg.inv(akeep[i])
        Aqinv[i]=np.linalg.inv(akeep[i].T.conj())
        aout1[i]=np.dot(np.dot(Apinv[i],akeep[i]),Aqinv[i])

    aout1=(aout1.reshape((na,nt,nf,2,2))).copy()
    print aout0-aout1

    # K=np.array(map(np.kron, Apinv, Aqinv)).reshape(S)
    # timer.timeit()



    # BatchInvert2(A)
    # timer.timeit()
    # BatchMatInverse_C.BatchInvert(A)
    # timer.timeit()


