#!/usr/bin/env python


import numpy as np
import Gaussian
import pylab
import scipy.optimize
import time
import ClassIslands
import ModColor
import pickle
import optparse
import ClassPointFit2 as ClassPointFit
#import ClassPointFit as ClassPointFit

from pyrap.images import image
from progressbar import ProgressBar
import reformat

def read_options():
    desc="""Questions and suggestions: cyril.tasse@obspm.fr"""
    global options
    opt = optparse.OptionParser(usage='Usage: %prog --ms=somename.MS <options>',version='%prog version 1.0',description=desc)
    group = optparse.OptionGroup(opt, "* Data-related options", "Won't work if not specified.")
    group.add_option('--im',help='Image name [no default]',default='')
    group.add_option('--Osm',help='Output Sky model [no default]',default='')
    group.add_option('--PSF',help='PSF (Majax,Minax,PA) in (arcsec,arcsec,deg). Default is %default',default="")
    group.add_option('--Pfact',help='PSF size multiplying factor. Default is %default',default="1")
    group.add_option('--DoPlot',help=' Default is %default',default="1")
    group.add_option('--DoPrint',help=' Default is %default',default="0")
    group.add_option('--Boost',help=' Boost is %default',default="3")
    group.add_option('--NCluster',help=' Boost is %default',default="0")
    group.add_option('--snr',help=' SNR above which we draw an island. Default is %default',default="10")
    group.add_option('--CMethod',help=' Cluster algorithm Method. Default is %default',default="1")
    opt.add_option_group(group)
    options, arguments = opt.parse_args()
    f = open("last_MakePModel.obj","wb")
    pickle.dump(options,f)
    
def main(options=None):
    if options==None:
        f = open("last_MakePModel.obj",'rb')
        options = pickle.load(f)

    Boost=int(options.Boost)
    CMethod=int(options.CMethod)
    NCluster=int(options.NCluster)
    Osm=options.Osm
    Pfact=float(options.Pfact)
    DoPlot=(options.DoPlot=="1")
    imname=options.im
    snr=float(options.snr)

    if Osm=="":
        Osm=reformat.reformat(imname,LastSlash=False)

    im=image(imname)
    PMaj=None
    try:
        PMaj=(im.imageinfo()["restoringbeam"]["major"]["value"])
        PMin=(im.imageinfo()["restoringbeam"]["minor"]["value"])
        PPA=(im.imageinfo()["restoringbeam"]["positionangle"]["value"])
        PMaj*=Pfact
        PMin*=Pfact
    except:
        print ModColor.Str(" No psf seen in header")
        pass

    if options.PSF!="":
        m0,m1,pa=options.PSF.split(',')
        PMaj,PMin,PPA=float(m0),float(m1),float(pa)
        PMaj*=Pfact
        PMin*=Pfact


    if PMaj!=None:
        print ModColor.Str(" - Using psf (maj,min,pa)=(%6.2f, %6.2f, %6.2f) (mult. fact.=%6.2f)"
                           %(PMaj,PMin,PPA,Pfact),col='green',Bold=False)
    else:
        print ModColor.Str(" - No psf info could be gotten from anywhere")
        print ModColor.Str("   use PSF keyword to tell what the psf is or is not")
        exit()


    ToSig=(1./3600.)*(np.pi/180.)/(2.*np.sqrt(2.*np.log(2)))
    PMaj*=ToSig
    PMin*=ToSig
    PPA*=np.pi/180

    b=im.getdata()[0,0,:,:]
    #b=b[3000:4000,3000:4000]#[120:170,300:370]
    c=im.coordinates()
    incr=np.abs(c.dict()["direction0"]["cdelt"][0])
    print ModColor.Str("   - Psf Size Sigma_(Maj,Min) = (%5.1f,%5.1f) pixels"%(PMaj/incr,PMin/incr),col="green",Bold=False)
        
    Islands=ClassIslands.ClassIslands(b,snr,Boost=Boost,DoPlot=DoPlot)
    Islands.FindAllIslands()
    
    ImOut=np.zeros_like(b)
    pBAR = ProgressBar('white', block='=', empty=' ',Title="Fit islands")

    #print "ion"
    #import pylab
    #pylab.ion()

    sourceList=[]
    for i in range(len(Islands.ListX)):
        comment='Isl %i/%i' % (i+1,len(Islands.ListX))
        pBAR.render(int(100* float(i+1) / len(Islands.ListX)), comment)

        xin,yin,zin=np.array(Islands.ListX[i]),np.array(Islands.ListY[i]),np.array(Islands.ListS[i])
        xm=int(np.sum(xin*zin)/np.sum(zin))
        ym=int(np.sum(yin*zin)/np.sum(zin))
        Fit=ClassPointFit.ClassPointFit(xin,yin,zin,psf=(PMaj/incr,PMin/incr,PPA),noise=Islands.Noise[xm,ym])
        sourceList+=Fit.DoAllFit()
        Fit.PutFittedArray(ImOut)

    Islands.FitIm=ImOut
    import rad2hmsdms
    xlist=[]
    ylist=[]
    slist=[]

    Cat=np.zeros((len(sourceList),),dtype=[('ra',np.float),('dec',np.float),('s',np.float)])
    Cat=Cat.view(np.recarray)
    isource=0

    for ijs in sourceList:
        i,j,s=ijs
        xlist.append(i)
        ylist.append(j)
        slist.append(s)
        f,d,dec,ra=im.toworld((0,0,i,j))
        Cat.ra[isource]=ra
        Cat.dec[isource]=dec
        Cat.s[isource]=s
        isource +=1
        #sra=rad2hmsdms.rad2hmsdms(ra,Type="ra").replace(" ",":")
        #sdec=rad2hmsdms.rad2hmsdms(dec,Type="dec").replace(" ",".")
        #print "%s, %s, %10.5f"%(sra,sdec,s)

    Islands.FittedComps=(xlist,ylist,slist)
    Islands.plot()

    import ClassSM
    SM=ClassSM.ClassSM(Osm,ReName=True,DoREG=True,SaveNp=True,NCluster=NCluster,DoPlot=DoPlot,FromExt=Cat,ClusterMethod=CMethod)
    #SM=ClassSM.ClassSM(Osm,ReName=True,SaveNp=True,DoPlot=DoPlot,FromExt=Cat)





if __name__=="__main__":
    read_options()
    main()
