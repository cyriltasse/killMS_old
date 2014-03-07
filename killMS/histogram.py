import numpy as np

def cumul(datain,nbins=100,minmax=(None,None)):
    m0,m1=minmax
    if m0==None: m0=np.min(datain)
    if m1==None: m1=np.max(datain)

    data=np.sort(datain).reshape(datain.size,1)
    xx=np.linspace(m0,m1,nbins)

    yy=np.sum((data<xx.reshape(1,nbins)),axis=0)
    yy=yy.astype(np.float32)/data.size

    return xx,yy

def hist(datain,nbins=100,minmax=(None,None)):
    m0,m1=minmax
    if m0==None: m0=np.min(datain)
    if m1==None: m1=np.max(datain)

    data=np.sort(datain).reshape(datain.size,1)
    xx=np.linspace(m0,m1,nbins)
    xx0=xx[0:-1]
    xx1=xx[1::]
    x0=(xx0+xx1)/2.

    cond0=data>xx0.reshape((1,nbins-1))
    cond1=data<xx1.reshape((1,nbins-1))
    yy=np.sum(cond0 & cond1,axis=0)
    yy=yy.astype(np.float32)/data.size

    return x0,yy

def test():
    import pylab
    x=np.random.randn(1000)
    xx,yy=hist(x)
    #pylab.plot(xx,yy)
    pylab.plot(xx,yy)
    pylab.draw()
    pylab.show()

if __name__=="__main__":
    test()
