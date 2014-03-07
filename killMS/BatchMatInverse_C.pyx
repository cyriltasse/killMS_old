from __future__ import division
import numpy as np
cimport numpy as np
import time
import numpy.linalg as linalg
#cimport numpy.linalg as linalg
import pylab

# import sys
# sys.path.append('/home/tasse/python_modules/tokyo_v0.3')
# import tokyo
# cimport tokyo

DTYPE_INT = np.int
ctypedef np.int_t DTYPE_INT_t

DTYPE_INT64 = np.int64
ctypedef np.int64_t DTYPE_INT64_t

DTYPE_COMPLEX128 = np.complex128
ctypedef np.complex128_t DTYPE_COMPLEX128_t

DTYPE_FLOAT64 = np.float64
ctypedef np.float64_t DTYPE_FLOAT64_t

DTYPE_FLOAT = np.float
ctypedef np.float_t DTYPE_FLOAT_t

# def tt():
#     return time.time()

# cdef inline int int_max(int a, int b): return a if a >= b else b
# cdef inline int int_min(int a, int b): return a if a <= b else b
# cdef inline double timeit(double t0, int step):
#     cdef double t1
#     t1=tt()
#     print "step_%i: %f"%(step, (t1-t0)*1000.)
#     return t1

    
cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)


# def Substract(np.ndarray[DTYPE_COMPLEX128_t, ndim=3, mode="c"] Kprod not None,
#               np.ndarray[DTYPE_COMPLEX128_t, ndim=1] SolsIon not None,
#               complex V,
#               np.ndarray[DTYPE_COMPLEX128_t, ndim=2] Zjones not None):                       

def BatchInvert(np.ndarray[DTYPE_COMPLEX128_t, ndim=3] A not None):                       

    
    cdef int i

    for i from 0 <= i < A.shape[0]:
        #sub=<complex>(Kprod[a0,a1,ind_np0,dd,tbin_desc])*<complex>(SourceFlux[dd])*<complex>(np.conjugate(Zjones[a1,dd]))
        A[i][:,:]=linalg.inv(A[i][:,:])

    return A 
        
cdef extern from "complex.h":
    #np.complex128_t conj(np.complex128_t z)
    complex conj(complex z)

@cython.boundscheck(False)
def FastInv(np.ndarray[complex, ndim=3] A, np.ndarray[complex, ndim=3] B, int H):
    cdef int N = A.shape[0]
    cdef unsigned int i = 0
    cdef complex ff,a,b,c,d
    for i from 0 <= i < N:
        if H==0:
            a=A[i, 0, 0]
            b=A[i, 0, 1]
            c=A[i, 1, 0]
            d=A[i, 1, 1]
        else:
            a=conj(A[i, 0, 0])
            b=conj(A[i, 1, 0])
            c=conj(A[i, 0, 1])
            d=conj(A[i, 1, 1])
            
        ff=1./((a*d-c*b))
        B[i, 0, 0]=ff*d
        B[i, 0, 1]=-ff*b
        B[i, 1, 0]=-ff*c
        B[i, 1, 1]=ff*a


@cython.boundscheck(False)
def FastProd22(np.ndarray[complex, ndim=3] A, np.ndarray[complex, ndim=3] B, np.ndarray[complex, ndim=3] Out):
    cdef int N = A.shape[0]
    cdef unsigned int i = 0
    cdef complex a,b,c,d
    for i from 0 <= i < N:
        a0=A[i, 0, 0]
        b0=A[i, 0, 1]
        c0=A[i, 1, 0]
        d0=A[i, 1, 1]

        a1=B[i, 0, 0]
        b1=B[i, 0, 1]
        c1=B[i, 1, 0]
        d1=B[i, 1, 1]

        Out[i, 0, 0]=a0*a1+b0*c1
        Out[i, 0, 1]=a0*b1+b0*d1
        Out[i, 1, 0]=c0*a1+d0*c1
        Out[i, 1, 1]=c0*b1+d0*d1


def Prod22(np.ndarray[complex, ndim=2] A, np.ndarray[complex, ndim=2] B, np.ndarray[complex, ndim=2] Out, int H):
    if H==0:
        Out[0, 0]=A[0, 0]*B[0, 0]+A[0, 1]*B[1, 0]
        Out[0, 1]=A[0, 0]*B[0, 1]+A[0, 1]*B[1, 1]
        Out[1, 0]=A[1, 0]*B[0, 0]+A[1, 1]*B[1, 0]
        Out[1, 1]=A[1, 0]*B[0, 1]+A[1, 1]*B[1, 1]
    if H==1:
        Out[0, 0]=A[0, 0]*conj(B[0, 0])+A[0, 1]*conj(B[0, 1])
        Out[0, 1]=A[0, 0]*conj(B[1, 0])+A[0, 1]*conj(B[1, 1])
        Out[1, 0]=A[1, 0]*conj(B[0, 0])+A[1, 1]*conj(B[0, 1])
        Out[1, 1]=A[1, 0]*conj(B[1, 0])+A[1, 1]*conj(B[1, 1])


#Sols=(na,nt,nf,2,2)
def FastApply(np.ndarray[complex, ndim=3] Vis, np.ndarray[double, ndim=1] TIME, np.ndarray[int, ndim=1] A0, np.ndarray[int, ndim=1] A1, np.ndarray[complex, ndim=3] Out, np.ndarray[complex, ndim=5] Gains, double t0sols, double t1sols, int SelChanSol):
    cdef int Nrows = Vis.shape[0]
    cdef int Nchan = Vis.shape[1]
    cdef unsigned int irow = 0
    cdef unsigned int ichan = 0

    cdef np.ndarray[complex, ndim=2] tmp=np.zeros((2,2), dtype=complex)
    cdef np.ndarray[complex, ndim=2] tmpSol0=np.zeros((2,2), dtype=complex)
    cdef np.ndarray[complex, ndim=2] tmpSol1=np.zeros((2,2), dtype=complex)

    cdef double time
    cdef double DT=t1sols-t0sols
    cdef unsigned int itime_sol,iA0, iA1
    
    for irow from 0 <= irow < Nrows:
        time=TIME[irow]
        itime_sol=int((time-t0sols)/DT)
        iA0=A0[irow]
        iA1=A1[irow]
        tmpSol0=Gains[iA0,itime_sol,SelChanSol]
        tmpSol1=Gains[iA1,itime_sol,SelChanSol]
        
        for ichan from 0 <= ichan < Nchan:
            tmp=Vis[irow,ichan]
            Prod22(tmpSol0,tmp,tmp,0)
            Prod22(tmp,tmpSol1,tmp,1)
            Vis[irow,ichan]=tmp

