import numpy as np
import scipy.ndimage as ndi
import os
import sys
from pyrap.images import image
import pyfits

def find_rms(m):
    rmsold=np.std(m)
    diff=1e-1
    cut=3.
    bins=np.arange(np.min(m),np.max(m),(np.max(m)-np.min(m))/30.)
    med=np.median(m)
    for i in range(10):
        ind=np.where(np.abs(m-med)<rmsold*cut)[0]
        rms=np.std(m[ind])
        if np.abs((rms-rmsold)/rmsold)<diff: break
        rmsold=rms
    return rms

def fill_noise(imname):
    #os.system("cp -r "+imname+" "+imname+".noise")
    #imname+=".noise"
    im=image(imname)
    #im.saveas(imname+".casa")

    #imname+=".casa"
    #im=image(imname)

    A=im.getdata()
    
    for pol in range(A.shape[1]):
        Avec=A[0,pol].flatten()
        ind=np.where(np.abs(Avec)>1e-8)[0]
        Avec=Avec[ind]
        rms=find_rms(Avec)
        print "pol=",rms
        imnoise=np.random.randn(A.shape[2],A.shape[2])*rms

        
        #img = ndi.gaussian_filter(img, (consize,consize))
        ind=np.where(A[0,pol]<1e-8)
        A[0,pol][ind]=imnoise[ind]

    im.putdata(A)
    imout=imname+".noise"
    print "   Saving result in: ",imout
    im.saveas(imout)

def fill_noiseFITS(imname):
    #os.system("cp -r "+imname+" "+imname+".noise")
    #imname+=".noise"
    im=pyfits.open(imname)[0]
    #im.saveas(imname+".casa")

    #imname+=".casa"
    #im=image(imname)

    A=im.data
    
    for pol in range(A.shape[1]):
        Avec=A[0,pol].flatten()
        ind=np.where(np.abs(Avec)>1e-8)[0]
        Avec=Avec[ind]
        rms=find_rms(Avec)
        print "pol=",rms
        imnoise=np.random.randn(A.shape[2],A.shape[2])*rms

        
        #img = ndi.gaussian_filter(img, (consize,consize))
        ind=np.where(np.abs(A[0,pol])<1e-8)
        A[0,pol][ind]=imnoise[ind]

    imout=imname+".noise"
    print "   Saving result in: ",imout
    im.writeto(imout,clobber=1)

if __name__=="__main__":
    imname=sys.argv[1]
    os.system("cp -r "+imname+" "+imname+".copy")
    imname+=".copy"
    
    if "fits" in imname.lower():
        fill_noiseFITS(imname)
    else:
        fill_noise(imname)
    
