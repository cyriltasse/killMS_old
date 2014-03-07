
import numpy as np
import scipy.fftpack
F=scipy.fftpack.fft
iF=scipy.fftpack.ifft
Fs=scipy.fftpack.fftshift
iFs=scipy.fftpack.ifftshift

F2=scipy.fftpack.fft2
iF2=scipy.fftpack.ifft2
getfreq=scipy.fftpack.fftfreq


def test():
    import pylab
    pylab.ion()
    pylab.clf()
    x=np.linspace(0.,100,200)
    y=2.*np.exp(1j*2.*np.pi*x/20.)
    pylab.subplot(2,2,1)
    pylab.plot(x,y.real,color="blue")
    pylab.plot(x,y.imag,color="green")

    f,freq=fft(y,dt=x[1]-x[0])

    pylab.subplot(2,2,2)
    pylab.plot(freq,f.real,color="blue")
    pylab.plot(freq,f.imag,color="green")
    
    ifs=ifft(f)
    pylab.subplot(2,2,3)
    pylab.plot(x,ifs.real,color="blue")
    pylab.plot(x,ifs.imag,color="green")
    pylab.plot(x,y.real,color="black",ls=":")
    pylab.plot(x,y.imag,color="black",ls=":")
    pylab.draw()
    pylab.show()

def test2():
    n=501
    theta=np.linspace(0.,2.*np.pi,200)
    grid=np.zeros((n,n),dtype=np.complex)
    off=(grid.shape[0])/2.
    r=np.linspace(.1,5.,30)#np.array([1.,2.,3.])
    l,m=0.5,0.5



    l,m=60.*np.pi/180,90.*np.pi/180#deg
    # D=5.*np.pi/180
    # factDiam=D


    u=(np.cos(theta)*r.reshape((r.size,1))).flatten()
    v=(np.sin(theta)*r.reshape((r.size,1))).flatten()
    umax=10
    up=off*u/umax+off
    vp=off*v/umax+off
    upm=-off*u/umax+off
    vpm=-off*v/umax+off
    vis=np.exp(-1j*2.*np.pi*(u*l+v*m))

    grid[np.int64(up),np.int64(vp)]+=vis
    grid[np.int64(upm),np.int64(vpm)]+=vis.conj()

    for i in range(up.shape[0]):
        grid[np.int64(up[i]),np.int64(vp[i])]+=vis[i]
        grid[np.int64(upm[i]),np.int64(vpm[i])]+=vis[i].conj()

#    grid.fill(0.)


    # grid.fill(0.)
    # grid[51,51]=1+1j
    # grid[49,49]=1-1j
    import pylab
    pylab.ion()
    pylab.clf()

    pylab.subplot(2,4,1)
    pylab.imshow(grid.real,interpolation="nearest")
    pylab.subplot(2,4,5)
    pylab.imshow(grid.imag,interpolation="nearest")

    im=fft2(grid)

    pylab.subplot(2,4,2)
    pylab.imshow(im.real,interpolation="nearest")
    pylab.colorbar()
    pylab.subplot(2,4,6)
    pylab.imshow(im.imag,interpolation="nearest")
    pylab.colorbar()
    
    ifs=ifft2(im)
    pylab.subplot(2,4,3)
    pylab.imshow(ifs.real,interpolation="nearest")
    pylab.subplot(2,4,7)
    pylab.imshow(ifs.imag,interpolation="nearest")

    pylab.subplot(2,4,4)
    pylab.imshow((ifs-grid).real,interpolation="nearest")
    pylab.subplot(2,4,8)
    pylab.imshow((ifs-grid).imag,interpolation="nearest")

#    pylab.tight_layout()
    pylab.draw()
    pylab.show()


# import pyfftw
# class FFTM():
#     def __init__(self,n):
#         pyfftw.interfaces.cache.enable()
#         self.a = pyfftw.n_byte_align_empty(n, 16, 'complex128')
        
#     def fft(self,A,dt=1):
#         self.a[:] = A.reshape((A.size,))
#         return pyfftw.interfaces.numpy_fft.fft(self.a),freq(A,dt)
        
# class FFTM2():
#     def __init__(self,A):
#         pyfftw.interfaces.cache.enable()
#         self.a = pyfftw.n_byte_align_empty(A.shape, 16, 'complex128')
#         self.b = pyfftw.n_byte_align_empty(A.shape, 16, 'complex128')
#         self.fft_object_a = pyfftw.FFTW(self.a, self.b)
        
#     def fft(self,A,dt=1):
#         self.a[:] = A[:]
        
#         self.fft_object_a()
#         out=np.zeros_like(A)
#         out[:]=self.b[:]
#         out=Fs(out,axes=-1)
#         return out,freq(A,dt)

#        return pyfftw.interfaces.numpy_fft.fft(self.a),freq(A,dt)
    
def fft(A,dt=1,Freq=True):
#    if len(A.shape)!=1: exit()
    a=F(A.astype(complex),axis=-1)
    FA= Fs(a,axes=-1)/A.shape[0]
    if Freq:
        return FA,freq(A,dt)
    else:
        return FA

def freq(A,dt):
    return Fs(scipy.fftpack.fftfreq(A.shape[0], d=dt))

def ifft(FA):
    if len(FA.shape)!=1: exit()
    #FFA=ifft2(ifftshift(FA))*FA.shape[0]**2
    #FFA= Fs( iF( iFs( FA ) ) )*FA.shape[0]
    FFA= iF( iFs( FA.astype(complex) ) ) *FA.shape[0]
    return FFA

#=================================

def fftOK(A,dt=1,Freq=True):
    a=F(iFs(A.astype(complex),axes=-1),axis=-1)
    FA= Fs(a,axes=-1)/A.shape[-1]
    if Freq:
        return FA,freq(A,dt)
    else:
        return FA

def ifftOK(FA):
    #FFA=ifft2(ifftshift(FA))*FA.shape[0]**2
    #FFA= Fs( iF( iFs( FA ) ) )*FA.shape[0]
    FFA= Fs(iF( iFs( FA.astype(complex) ,axes=-1),axis=-1),axes=-1) *FA.shape[-1]
    return FFA

#============= 2D case =============

def fft2(A):
    if len(A.shape)!=2: exit()
    #FA=fftshift(fft2(A))
    FA= Fs(F2(iFs(A)))/A.shape[0]**2
    #FA= Fs(F2(iFs(A)))/A.shape[0]**2
    return FA

def ifft2(FA):
    if len(FA.shape)!=2: exit()
    #FFA=ifft2(ifftshift(FA))*FA.shape[0]**2
    FFA= Fs(iF2(iFs(FA)))*FA.shape[0]**2
    #FFA= iF2(iFs(FA))*FA.shape[0]**2

    return FFA


