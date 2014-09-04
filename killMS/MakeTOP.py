import sys
import pylab
import numpy as np
import numpy.linalg as linalg
import scipy.fftpack as FFT
import time as time_mod
import os
import scipy.optimize
import timeit
import numexpr as ne

        
class ClassMakeTOP():
    def __init__(self,PMachine,SolvePolMode="I"):
        self.PM=PMachine
        self.MS=PMachine.MS
        self.SM=PMachine.SM
        self.SolvePolMode=SolvePolMode
        self.weigths=np.array(self.SM.WeightDir.tolist()*self.MS.na)
        #self.weigths.fill(1)

    def make_A0new(self,row0,row1):
        ant0=self.MS.A0[row0:row1]
        ant1=self.MS.A1[row0:row1]
        Ntimes=(row1-row0)/self.MS.nbl
        na=self.MS.na
        nbl=self.MS.nbl
        NDir=self.SM.NDir
        uvw=self.MS.uvw[row0:row1]
        NSPWChan=self.MS.NSPWChan
        SourceCat=self.SM.SourceCat
        dt=self.MS.dt
        DT=self.MS.times_all[row1]-self.MS.times_all[row0]

        A0mat=np.zeros((NSPWChan*Ntimes*na,NDir*na),dtype=np.complex)
        Amat=np.zeros((NSPWChan*Ntimes*na,NDir*na),dtype=np.complex)
        vv=np.zeros((uvw.shape[0],),dtype=np.complex)
        alpha=0.
        exp=np.exp
        flag=self.MS.flag_all
        for i in range(self.SM.NDir):
            #print "idir=%i, 1./sqrt(weigth)=%f"%(i,weigth)
            for spw in range(NSPWChan):
                vv.fill(0.)

                ff=np.logical_and(flag[spw][row0:row1,0],flag[spw][row0:row1,3])

                vv=self.PM.PredictDirSPW(self.SM.Dirs[i],spw,uvw=uvw,flags=ff)
                #vv=self.PM.PredictDirSPW(i,spw,uvw=uvw,flags=ff)
                #vv[(ff==True)|(PM.)]=0.
                noise=(np.random.randn(vv.shape[0])+1j*np.random.randn(vv.shape[0]))*1e-6

                indFlag=(ff==True)
                vv[indFlag]=noise[indFlag]
                #vv[indFlag]=0.
                #indFlag=self.PM.FlagPredict
                #vv[indFlag]=noise[indFlag]
    
                for bl in range(nbl):
                    a0,a1=ant0[bl],ant1[bl]
                    if a0==a1: continue
                    
                    icoord=spw*Ntimes+a0*NSPWChan*Ntimes
                    jcoord=i+a1*NDir
                    #A0mat[icoord:icoord+Ntimes,jcoord]=vv[bl::nbl]
                    weight=1./np.sqrt(self.weigths[jcoord])
                    A0mat[icoord:icoord+Ntimes,jcoord]=weight*vv[bl::nbl]
                    icoord=spw*Ntimes+a1*NSPWChan*Ntimes
                    jcoord=i+a0*NDir
                    #A0mat[icoord:icoord+Ntimes,jcoord]=vv[bl::nbl].conj()
                    weight=1./np.sqrt(self.weigths[jcoord])
                    A0mat[icoord:icoord+Ntimes,jcoord]=weight*vv[bl::nbl].conj()
        return A0mat,Amat
    
    
    def make_A0newList(self,row0,row1):
        ant0=self.MS.A0[row0:row1]
        ant1=self.MS.A1[row0:row1]
        Ntimes=(row1-row0)/self.MS.nbl
        na=self.MS.na
        nbl=self.MS.nbl
        NDir=self.SM.NDir
        uvw=self.MS.uvw[row0:row1]
        NSPWChan=self.MS.NSPWChan
        SourceCat=self.SM.SourceCat
        dt=self.MS.dt
        DT=self.MS.times_all[row1]-self.MS.times_all[row0]

        A0matList=[]
        AmatList=[]


        Amat=np.zeros((NSPWChan*Ntimes*na,NDir*na),dtype=np.complex)
        vv=np.zeros((uvw.shape[0],),dtype=np.complex)
        alpha=0.
        exp=np.exp
        flag=self.MS.flag_all
        for iant in range(na):
            P=np.zeros((NSPWChan*Ntimes*na,NDir),dtype=np.complex)
            A0matList.append(P)
            AmatList.append(P.copy())
            
        for i in range(self.SM.NDir):
            #print "idir=%i, 1./sqrt(weigth)=%f"%(i,weigth)
            for spw in range(NSPWChan):
                vv.fill(0.)

                ff=np.logical_and(flag[spw][row0:row1,0],flag[spw][row0:row1,3])

                vv=self.PM.PredictDirSPW(self.SM.Dirs[i],spw,uvw=uvw,flags=ff)
                #vv=self.PM.PredictDirSPW(i,spw,uvw=uvw,flags=ff)
                #vv[(ff==True)|(PM.)]=0.
                noise=(np.random.randn(vv.shape[0])+1j*np.random.randn(vv.shape[0]))*1e-6

                indFlag=(ff==True)
                vv[indFlag]=noise[indFlag]
                #vv[indFlag]=0.
                #indFlag=self.PM.FlagPredict
                #vv[indFlag]=noise[indFlag]
    
                for bl in range(nbl):
                    a0,a1=ant0[bl],ant1[bl]
                    if a0==a1: continue
                    
                    icoord=spw*Ntimes+a0*NSPWChan*Ntimes
                    jcoord=i+a1*NDir
                    weight=1./np.sqrt(self.weigths[jcoord])
                    A0matList[a1][icoord:icoord+Ntimes,i]=weight*vv[bl::nbl]
                    #A0matList[a1][icoord:icoord+Ntimes,i]=vv[bl::nbl]

                    icoord=spw*Ntimes+a1*NSPWChan*Ntimes
                    jcoord=i+a0*NDir
                    weight=1./np.sqrt(self.weigths[jcoord])
                    A0matList[a0][icoord:icoord+Ntimes,i]=weight*vv[bl::nbl].conj()
                    #A0matList[a0][icoord:icoord+Ntimes,i]=vv[bl::nbl].conj()


        return A0matList,AmatList
    
    
    
    
    def give_AnewList(self,x,A0mat,Amat,Ntimes):
        na=self.MS.na
        nbl=self.MS.nbl
        NDir=self.SM.NDir
        NSPWChan=self.MS.NSPWChan

        #Amat.fill(0.)
        AmatOut=[]
        gains_mat=[]
        NrowBlock=Ntimes*NSPWChan
        gains_mat=np.zeros((NrowBlock*na,NDir),dtype=np.complex)
        for i in range(NDir):
            for a0 in range(na):
                gains_mat[a0*NrowBlock:a0*NrowBlock+NrowBlock,i]=x[i+a0*NDir]
                
        for i in range(na):
            icoord=0
            jcoord=i*NDir
            #Amat[icoord:icoord+NrowBlock*na,jcoord:jcoord+NDir]=gains_mat*A0mat[icoord:icoord+NrowBlock*na,jcoord:jcoord+NDir]
            Amat[i]=A0mat[i]*gains_mat

        return Amat#A0mattuple(AmatOut)
    
    def give_Anew(self,x,A0mat,Amat,Ntimes):
        na=self.MS.na
        nbl=self.MS.nbl
        NDir=self.SM.NDir
        NSPWChan=self.MS.NSPWChan

        Amat.fill(0.)
        NrowBlock=Ntimes*NSPWChan
        gains_mat=np.zeros((NrowBlock*na,NDir),dtype=np.complex)
        for i in range(NDir):
            for a0 in range(na):
                gains_mat[a0*NrowBlock:a0*NrowBlock+NrowBlock,i]=x[i+a0*NDir]
                
        for i in range(na):
            icoord=0
            jcoord=i*NDir
            Amat[icoord:icoord+NrowBlock*na,jcoord:jcoord+NDir]=gains_mat*A0mat[icoord:icoord+NrowBlock*na,jcoord:jcoord+NDir]
        return Amat
    
    def give_b_Pnew(self,row0,row1,pol=0):
        import ClassTimeIt
#        timer=ClassTimeIt.ClassTimeIt()
        na=self.MS.na
        nbl=self.MS.nbl
        NSPWChan=self.MS.NSPWChan

        visin=self.MS.data
        uvw=self.MS.uvw[row0:row1]
        Ntimes=(row1-row0)/nbl
        Nrow=uvw.shape[1]
        ant0=self.MS.A0[row0:row1]
        ant1=self.MS.A1[row0:row1]

        if self.SolvePolMode=="I":
            vv=np.array((visin[:,row0:row1,0]+visin[:,row0:row1,3])/2.,dtype=np.complex)
            #vv=np.array(visin[:,row0:row1,3]/2.,dtype=np.complex)
        else:
            vv=np.array(visin[:,row0:row1,pol],dtype=np.complex)
    
        #select baseline, compute fft
        
        #This is just the scallar phase term 
        b=np.zeros((Ntimes*NSPWChan*na*na,),dtype=np.complex)
        Pscal=0.
        coef=0.
        ind_all=np.arange(ant0.shape[0])
        #stop

        for spw in range(NSPWChan):
            for bl in range(nbl):
                a0,a1=ant0[bl],ant1[bl]
                if a0==a1: continue
                icoord=spw*Ntimes+a0*NSPWChan*Ntimes+a1*NSPWChan*Ntimes*na
                b[icoord:icoord+Ntimes]=vv[spw,bl::nbl]
                icoord=spw*Ntimes+a1*NSPWChan*Ntimes+a0*NSPWChan*Ntimes*na
                b[icoord:icoord+Ntimes]=vv[spw,bl::nbl].conj()

        return b
    
    def give_b_P(self,row0,row1,pol=0):
        import ClassTimeIt
#        timer=ClassTimeIt.ClassTimeIt()
        na=self.MS.na
        nbl=self.MS.nbl
        NSPWChan=self.MS.NSPWChan

        visin=self.MS.data
        uvw=self.MS.uvw[row0:row1]
        Ntimes=(row1-row0)/nbl
        Nrow=uvw.shape[1]
        ant0=self.MS.A0[row0:row1]
        ant1=self.MS.A1[row0:row1]

        if self.SolvePolMode=="I":
            vv=np.array((visin[:,row0:row1,0]+visin[:,row0:row1,3])/2.,dtype=np.complex)
            #vv=np.array(visin[:,row0:row1,3]/2.,dtype=np.complex)
        else:
            vv=np.array(visin[:,row0:row1,pol],dtype=np.complex)
    
        #select baseline, compute fft
        
        #This is just the scallar phase term 
        b=np.zeros((Ntimes*NSPWChan*na*na,),dtype=np.complex)
        Pscal=0.
        coef=0.
        import numexpr as ne
        ind_all=np.arange(ant0.shape[0])
        #stop
        for a0 in range(na):
            for a1 in range(na):
                if a0==a1: continue
#                timer.reinit()
                ind_bl=np.where((ant0==a0)&(ant1==a1))[0]
                #ind_bl=ind_all[ne.evaluate("where((ant0==a0)&(ant1==a1),True,False)")]
                dodonj=False
                domap=True
#                timer.timeit("first0")
                if ind_bl.shape[0]==0:
                    ind_bl=np.where((ant1==a0)&(ant0==a1))[0]
                    #ind_bl=ind_all[ne.evaluate("where((ant1==a0)&(ant0==a1),True,False)")]
                    dodonj=True
                    domap=False
#                timer.timeit("first")
                for chan in range(NSPWChan):
                    icoord=chan*Ntimes+a0*NSPWChan*Ntimes+a1*NSPWChan*Ntimes*na
                    vvv=vv[chan,ind_bl].copy()
                    if dodonj==True: vvv=vvv.conj()
                    b[icoord:icoord+Ntimes]=vvv
                    # if domap==True:
                    #     maping_row[icoord:icoord+Ntimes]=ind_bl
                    #     maping_chan[icoord:icoord+Ntimes]=chan
                    
                    # Pscal+=self.find_rms(b[icoord:icoord+Ntimes])
                    # coef+=1
                # timer.timeit("second")
                # print
                
        #Pscal/=coef
        #Pscal=np.std(b)
        #invcov=1./Pscal**2
    
    
    
        return b#,invcov,maping_row,maping_chan
    
            
    
    
    def find_rms(self,m):
        rmsold=np.std(m)
        diff=1e-1
        cut=3.
        med=np.median(m)
        rms=0.
        for i in range(10):
            ind=np.where(np.abs(m-med)<rmsold*cut)[0]
            if ind.shape[0]<2: break
            if np.max(np.abs(m[ind]))==0.: break
            rms=np.std(m[ind])
            if np.abs((rms-rmsold)/rmsold)<diff: break
            rmsold=rms
        return rms
