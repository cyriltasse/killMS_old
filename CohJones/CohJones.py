#!/usr/bin/env python

import optparse
import sys
import MyPickle
#import logo

sys.path=[name for name in sys.path if not(("pyrap" in name)&("/usr/local/lib/" in name))]

# test

#import numpy
#print numpy.__file__
#import pyrap
#print pyrap.__file__
#stop


import ModColor
if "nocol" in sys.argv:
    print "nocol"
    ModColor.silent=1
if "nox" in sys.argv:
    import matplotlib
    matplotlib.use('agg')
    print ModColor.Str(" == !NOX! ==")

import time
import os
import numpy as np
import pickle
import ClassMS
import ClassSM
from ClassPredict import ClassPredict
import PseudoKill
import ClassTimeIt

def read_options():
    desc="""CohJones Questions and suggestions: cyril.tasse@obspm.fr"""
    
    opt = optparse.OptionParser(usage='Usage: %prog --ms=somename.MS <options>',version='%prog version 1.0',description=desc)
    group = optparse.OptionGroup(opt, "* Data-related options", "Won't work if not specified.")
    group.add_option('--ms',help='Input MS to draw [no default]',default='')
    group.add_option('--SkyModel',help='List of targets [no default]',default='')
    opt.add_option_group(group)
    
    # group = optparse.OptionGroup(opt, "* Data selection options", "ColName is set to DATA column by default, and other parameters select all the data.")
    group = optparse.OptionGroup(opt, "* Data selection options")
    group.add_option('--kills',help='Name or number index of sources to kill',default="")
    group.add_option('--invert',help='Invert the selected sources to kill',default="0")
    opt.add_option_group(group)
    
    group = optparse.OptionGroup(opt, "* Algorithm options", "Default values should give reasonable results, but all of them have noticeable influence on the results")
    group.add_option('--timestep',help='Time interval for a solution [minutes]. Default is %default. ',default=30)
    group.add_option('--NCPU',help=' Number of cores to use for the calibration of the Tikhonov output. Default is %default ',default="6")
    group.add_option('--niter',help=' Number of iterations for the solve. Default is %default ',default="20")
    #group.add_option('--doSmearing',help='Takes time and frequency smearing if enabled. Default is %default ',default="0")
    #group.add_option('--SolvePolMode',help=' Polarisation mode (I/All). Default is %default',default="I")
    #group.add_option('--ChanSels',help=' Channel selection. Default is %default',default="")
    #group.add_option('--BLFlags',help=' Baselines To be flagged. Default is %default',default="")
    group.add_option('--Restore',help=' Restore BACKUP in CORRECTED. Default is %default',default="0")
    #group.add_option('--LOFARBeamParms',help='Applying the LOFAR beam parameters [Mode[A,AE,E],TimeStep]. Default is %default',default="")
    group.add_option('--LOFARBeamParms',help='Not Working yet',default="")

    group.add_option('--TChunk',help=' Time Chunk in hours. Default is %default',default="15")
    group.add_option('--SubOnly',help=' Only substract the skymodel. Default is %default',default="0")
    group.add_option('--DoBar',help=' Draw progressbar. Default is %default',default="1")
    group.add_option('--InCol',help=' Column to work on. Default is %default',default="CORRECTED_DATA_BACKUP")
    group.add_option('--ApplyCal',help=' Apply direction averaged gains to residual data. Default is %default',default="0")
    


    opt.add_option_group(group)
    
    
    options, arguments = opt.parse_args()
    
    f = open("last_killMS.obj","wb")
    pickle.dump(options,f)
    

def main(options=None):
    

    if options==None:
        f = open("last_killMS.obj",'rb')
        options = pickle.load(f)
    
    ApplyCal=(options.ApplyCal=="1")

    if options.ms=="":
        print "Give an MS name!"
        exit()
    if options.SkyModel=="":
        print "Give a Sky Model!"
        exit()
    if not(".npy" in options.SkyModel):
        print "Give a numpy sky model!"
        exit()

    TChunk=float(options.TChunk)
    delta_time=float(options.timestep)
    niterin=int(options.niter)
    NCPU=int(options.NCPU)
    SubOnly=(int(options.SubOnly)==1)
    invert=(options.invert=="1")
    


        
    MS=ClassMS.ClassMS(options.ms,Col=options.InCol,ReOrder=True,EqualizeFlag=True,
                       DoReadData=0,TimeChunkSize=TChunk)#,RejectAutoCorr=True)
    MS.PutBackupCol()

    ApplyBeam=False
    LOFARBeamParms=None
    if options.LOFARBeamParms!="":
        Mode,BeamTimeStep=options.LOFARBeamParms.split(",")
        BeamTimeStep=float(BeamTimeStep)
        ApplyBeam=True
        LOFARBeamParms=Mode,BeamTimeStep
        useElementBeam=False
        useArrayFactor=False
        if "A" in Mode:
            useArrayFactor=True
        if "E" in Mode:
            useElementBeam=True
            print "doesn't work yet"
            exit()
            
        MS.LoadSR(useArrayFactor=useArrayFactor,useElementBeam=useElementBeam)

    if options.kills!="":
        kills=options.kills.split(",")
    else:
        invert=True
        kills=[]

    SM=ClassSM.ClassSM(options.SkyModel,infile_cluster="",killdirs=kills,invert=invert,solveFor=[],DoPrintCat=False)
    
    #PMachine=ClassPredict(MS,options.SkyModel,Cluster=options.ClusterList,NCluster=NCluster,NCPU=NCPU)
    PMachine=ClassPredict(MS,SM,NCPU=NCPU,LOFARBeamParms=LOFARBeamParms)
    
    timer=ClassTimeIt.ClassTimeIt()

    TimesInt=np.arange(0,MS.DTh,TChunk).tolist()
    if not(MS.DTh in TimesInt): TimesInt.append(MS.DTh)
    

    # import pylab
    # pylab.ion()
    SolsAll=[]
    for i in range(len(TimesInt)-1):
        if SubOnly:
            T0,T1=TimesInt[i],TimesInt[i+1]
            PMachine.MS.ReadData(t0=T0,t1=T1)
            print ModColor.Str(" Substract sky model in [%-.2f->%-.2f h]"%(T0,T1),Bold=False)
            PMachine.SM.SourceCat=PMachine.SM.SourceCat[PMachine.SM.SourceCat.kill==1]
            Vis=PMachine.predict(Return=True)
            MS.data-=Vis
        else:

            
            PMachine.MS.ReadData(t0=TimesInt[i],t1=TimesInt[i+1])

            if SM.ExistToSub and not(ApplyCal):
                SM.RestoreCat()
                SM.SelectSubCat(SM.SourceCat.kill==-1)
                Vis=PMachine.predict(Return=True)
                MS.data-=Vis

            SM.RestoreCat()
            SM.SelectSubCat(SM.SourceCat.kill!=-1)

            Sols=PseudoKill.PseudoKill(PMachine,delta_time=delta_time,NCPU=NCPU,niterin=niterin,T0=TimesInt[i],T1=TimesInt[i+1],PrintProps=i)
            T0,T1=TimesInt[i],TimesInt[i+1]
            SolsAll.append({"T0":T0,"T1":T1,"Sols":Sols})
            np.save("Sols",np.array(Sols))

            #print "no kiill!!!"
            #print "SELCAT!!!!"
            #print "caca",PMachine.SM.SourceCat.kill
            PMachine.SM.SourceCat=PMachine.SM.SourceCat[PMachine.SM.SourceCat.kill==1]


            Vis=PMachine.predict(Sols,Return=True)

            # import pylab
            # res=MS.data-Vis
            # pylab.clf()
            # pylab.subplot(2,1,1)
            # pylab.plot(MS.data[0,:,0].real,color="black")
            # pylab.plot(Vis[0,:,0].real,color="blue")
            # pylab.plot(res[0,:,0].real,color="red")
            # pylab.subplot(2,1,2)
            # pylab.plot(MS.data[0,:,0].imag,color="black")
            # pylab.plot(Vis[0,:,0].imag,color="blue")
            # pylab.plot(res[0,:,0].imag,color="red")
            # pylab.draw()
            # pylab.show(False)

            MS.data-=Vis


        if ApplyCal:
            nrows=MS.nrows
            Row0=0
            Row1=nrows
            TVec=MS.times_all[Row0:Row1]
            A0Vec=MS.A0[Row0:Row1]
            A1Vec=MS.A1[Row0:Row1]
            gg=Sols.GiveRawSols(TVec,A0Vec,A1Vec,idir=0)
            for spw in range(MS.NSPWChan):
                MS.data[spw,:,0]/=gg
                MS.data[spw,:,3]/=gg

        
        MS.SaveVis(DoPrint=False)
        

    MyPickle.Save(SolsAll,"%s_Sols.pickle"%MS.MSName)

    



def Restore(options=None):
    if options==None:
        f = open("last_killMS.obj",'rb')
        options = pickle.load(f)
    MS=ClassMS.ClassMS(options.ms)
    MS.Restore()

#     KalmanKill.set_chanOptions(options)
#     #KalmanKill.zero_chans(options)

if __name__=="__main__":
    read_options()
    f = open("last_killMS.obj",'rb')
    options = pickle.load(f)
    if options.DoBar=="0":
        from progressbar import ProgressBar
        ProgressBar.silent=1
    # else:
    #     os.system('clear')

    if options.Restore=="1":
        Restore(options)
    else:
        #logo.print_logo()
        main(options=options)
