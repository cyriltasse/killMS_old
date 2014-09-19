
import numpy as np
import ModColor
import gnumpy

try:
    import cudamat as cm
    print ModColor.Str("Cudamat found!!!","green")
    DoCud=True
except:
    print ModColor.Str("Could not find cudamat!!!"), "using numpy instead"
    DoCud=False

    

def CudaDot(a,b):
    cm.cublas_init()
    gm1 = cm.CUDAMatrix(a)
    gm2 = cm.CUDAMatrix(b)
    gm = cm.dot(gm1, gm2)
    arr=gm.asarray()
    cm.shutdown()
    return arr

def dot(a,b):
    if (DoCud)&(a.size>1000):
        return CudaDot(a,b)
    else:
        return np.dot(a,b)

def test():
    import ClassTimeIt

    import pycuda.autoinit
    import pycuda.gpuarray as gpuarray
    import numpy as np
    import scikits.cuda.linalg as culinalg
    culinalg.init()


    T=ClassTimeIt.ClassTimeIt()
    smax=2000
    Sx=np.int64(np.linspace(32,2000,20))
    Ltcpu=[]
    Ltgpu1=[]
    Ltgpu2=[]
    Ltgpu3=[]

    cm.cublas_init()
    a=np.array(np.random.randn(2,2),dtype=np.float32,order="F")
    a0=gnumpy.garray(a)


    for sx in Sx:
        gnumpy.free_reuse_cache()
        print gnumpy.memory_in_use()/1024.**3

        print "%i/%i"%(sx,1000)
        a=np.array(np.random.randn(sx,sx),dtype=np.float32,order="F")
#        a=np.ones((3000,3000),dtype=np.float32, order='F')
        b=a.copy()

        T.reinit()
        Pnp=np.dot(a,b)
        t_cpu=T.timeit()


        T.reinit()
#        dot(a,b)
        gm1 = cm.CUDAMatrix(a)
        gm2 = cm.CUDAMatrix(b)
        gm = cm.dot(gm1, gm2)
        arr=gm.asarray()
        t_gpu1=T.timeit()

        print "error cudamat = %f"%np.std(Pnp-arr)
        del gm, gm1, gm2

        T.reinit()
        a0=gnumpy.garray(a)
        b0=gnumpy.garray(b)
        c=gnumpy.dot(a0,b0).asarray()
        t_gpu2=T.timeit()

        print "error gnumpy  = %f"%np.std(Pnp-c)
        del c

        T.reinit()
        a_gpu = gpuarray.to_gpu(a)
        b_gpu = gpuarray.to_gpu(b)
        c= culinalg.dot(a_gpu, b_gpu)
        cc=c.get()
        t_gpu3=T.timeit()


        Ltcpu.append(t_cpu)
        Ltgpu1.append(t_gpu1)
        Ltgpu2.append(t_gpu2)
        Ltgpu3.append(t_gpu3)
        del a, b
        



    cm.shutdown()

    

    import pylab
    pylab.clf()
    pylab.plot(Sx,Ltcpu)
    pylab.plot(Sx,Ltgpu1)
    pylab.plot(Sx,Ltgpu2)
    pylab.plot(Sx,Ltgpu3)
    pylab.legend(("dotblas numpy","cudamat","gnumpy","scikits"),loc=2)
    pylab.xlabel("Matrix size")
    pylab.ylabel("Time (sec.)")
    pylab.draw()
    pylab.show()


if __name__=="__main__":

    test()



