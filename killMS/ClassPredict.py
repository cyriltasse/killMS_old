import numpy as np
from pyrap.tables import table
from ClassMS import ClassMS
from ClassSM import ClassSM
from ClassTimeIt import ClassTimeIt
import numexpr as ne
#import ModNumExpr
from progressbar import ProgressBar
import multiprocessing

class ClassPredict():
    def __init__(self,MS,modelName,Cluster="",NCluster=0,NCPU=None,freqs=None):
        if type(MS)==str:
            self.MS=ClassMS(MS,Col="CORRECTED_DATA",ReOrder=True)
        else: 
            self.MS=MS # is a ClassMS!
        if type(modelName)==str:
            self.SM=ClassSM(modelName,infile_cluster=Cluster,NCluster=NCluster)
        else:
            self.SM=modelName

        self.NDir=self.SM.NDir
        self.CT=ClassTimeIt()
        if NCPU==None:
            self.NCPU=multiprocessing.cpu_count()-2
        else:
            self.NCPU=NCPU
        self.GaussMinFlux=0.#1e-6
        Title="Predict"
        toolbar_width = 50
        self.pBAR = ProgressBar('white', block='=', empty=' ',Title=Title)
        ne.set_num_threads(self.NCPU)
        self.KillSel=None
        self.freqs=self.MS.ChanFreq[0]
        self.wave=self.MS.wavelength_chan.flatten()
        if freqs!=None:
            self.freqs=freqs
            self.wave=299792458./freqs

    def predict(self,Sols=None,pBAR=True,SetAsAttribute=True,Row01=None,Return=False):

        if Row01!=None:
            Row0,Row1=Row01
            nrows=Row1-Row0
        else:
            nrows=self.MS.nrows
            Row0=0
            Row1=nrows

        SourceCat=self.SM.SourceCat

        NSPWChan=self.MS.NSPWChan
        #uvw=self.MS.uvw.copy()
        DataOut=np.zeros_like(self.MS.data[:,Row0:Row1,:])
        freq=self.MS.ChanFreq.flatten()
        pi=float(np.pi)
        #a = np.random.rand(1e6)+1j*np.random.rand(1e6)
        #ne.evaluate("exp(a)")

        uvwL=self.MS.uvw
        U=uvwL[Row0:Row1,0].astype(float).flatten().copy()
        V=uvwL[Row0:Row1,1].astype(float).flatten().copy()
        W=uvwL[Row0:Row1,2].astype(float).flatten().copy()

        if Sols!=None:
            TVec=self.MS.times_all[Row0:Row1]
            A0Vec=self.MS.A0[Row0:Row1]
            A1Vec=self.MS.A1[Row0:Row1]


        Dirs=list(set(SourceCat.Cluster.tolist()))
        NDir=len(Dirs)
        for spw in range(NSPWChan):
            self.DoneSource=0
            ColOut=np.zeros((nrows,),dtype=complex)
            dirindex=0
            for i in Dirs:
                #print i,"/",self.NDir
                ColOutDir=self.PredictDirSPW(i,spw,U=U,V=V,W=W,pBAR=pBAR)
                if Sols!=None:
                    gg=Sols.GiveRawSols(TVec,A0Vec,A1Vec,idir=dirindex)
                    ColOut=ne.evaluate("ColOut+gg*ColOutDir")
                else:
                    ColOut=ne.evaluate("ColOut+ColOutDir")
                dirindex+=1
            #ColOut*=2.
            DataOut[spw,:,0]+=ColOut
            DataOut[spw,:,3]+=ColOut

        if SetAsAttribute: self.DataOut=DataOut
        self.pBAR.reset()
        if Return: return DataOut

    def PredictDirSPW(self,idir,spw,flags=None,uvw=None,U=None,V=None,W=None,pBAR=False):

        SourceCat=self.SM.SourceCat

        freq=self.freqs
        pi=float(np.pi)
        wave=self.wave#[0]
        f0=complex(2*pi*1j/wave[spw])
        if uvw!=None:
            U=uvw[:,0].astype(float).flatten().copy()
            V=uvw[:,1].astype(float).flatten().copy()
            W=uvw[:,2].astype(float).flatten().copy()
        ColOut=np.zeros(U.shape,dtype=complex)
        f0=complex(2*pi*1j/wave[spw])

        ind0=np.where(SourceCat.Cluster==idir)[0]
        rasel =SourceCat.ra[ind0]
        decsel=SourceCat.dec[ind0]
        
        TypeSources=SourceCat.Type[ind0]
        Gmaj=SourceCat.Gmaj[ind0]
        Gmin=SourceCat.Gmin[ind0]
        Gangle=SourceCat.Gangle[ind0]
        Ssel  =SourceCat.Sref[ind0]*(freq[spw]/SourceCat.RefFreq[ind0])**(SourceCat.alpha[ind0])
        KillIt=SourceCat.kill[ind0]

        for dd in range(len(ind0)):
            l,m=self.MS.radec2lm_scalar(rasel[dd],decsel[dd])
            l=float(l)
            m=float(m)
            nn=float(np.sqrt(1.-l**2-m**2)-1.)
            f=float(Ssel[dd])
            
            KernelPha=ne.evaluate("f0*(U*l+V*m+W*nn)")
            f0b=float(2*pi/wave[spw])

            if TypeSources[dd]==1:
                import ClassPredict2
                ang=Gangle[dd]
                SigMaj=Gmaj[dd]
                SigMin=Gmin[dd]
                #uvp=ClassPredict2.giveGauss(U,V,SigMaj,SigMin,ang,freq)
                #fudge=1.0/np.sqrt(np.log(16.0))
                WaveL=wave[spw]
                SminCos=SigMin*np.cos(ang)
                SminSin=SigMin*np.sin(ang)
                SmajCos=SigMaj*np.cos(ang)
                SmajSin=SigMaj*np.sin(ang)
                up=ne.evaluate("U*SminCos-V*SminSin")
                vp=ne.evaluate("U*SmajSin+V*SmajCos")
                const=-(2*(pi**2)*(1/WaveL)**2)#*fudge
                uvp=ne.evaluate("const*((U*SminCos-V*SminSin)**2+(U*SmajSin+V*SmajCos)**2)")
                KernelPha=ne.evaluate("KernelPha+uvp")
            LogF=np.log(f)
            Kernel=ne.evaluate("exp(KernelPha+LogF)")
            ColOut=ne.evaluate("ColOut+Kernel")
            if pBAR==True:
                comment='src %i/%i, spw %i/%i' % (self.DoneSource+1,self.SM.NSources,spw+1,self.MS.NSPWChan)
                self.pBAR.render(int(100* float(self.DoneSource+1) / self.SM.NSources), comment)
                self.DoneSource+=1


            # import pylab
            # nn=100
            # pylab.clf()
            # pylab.scatter(U[1::nn],V[1::nn],c=np.abs(Kernel[1::nn]),vmin=0,vmax=1)
            # pylab.draw()
            # pylab.show()
            # stop

        #noise=(np.random.randn(ColOut.shape[0])+1j*np.random.randn(ColOut.shape[0]))*1e-6
        #ind=(flags==1)
        #ColOut[ind]=noise[ind]
        #self.FlagPredict=(np.abs(ColOut)<self.GaussMinFlux*np.max(np.abs(ColOut)))
        return ColOut

    def predictIon(self,CIon):
        SourceCat=self.SM.SourceCat
        Nchan=self.MS.Nchan
        uvw=self.MS.uvw
        DataOut=np.zeros_like(self.MS.data)
        wave=self.MS.wavelength_chan[0]
        freq=self.MS.ChanFreq[0]
        
        for i in range(self.NDir):
            ind0=np.where(SourceCat.Cluster==i)[0]
            rasel =SourceCat.ra[ind0]
            decsel=SourceCat.dec[ind0]
            for spw in range(Nchan):
                Ssel  =SourceCat.Sref[ind0]*(freq[spw]/SourceCat.RefFreq[ind0])**(SourceCat.alpha[ind0])
                for dd in range(len(ind0)):
                    l,m=self.MS.radec2lm_scalar(rasel[dd],decsel[dd])
                    self.CT.reinit()
                    Kernel=np.exp(2*np.pi*1j*(1./wave[spw])*(uvw[:,0]*l+uvw[:,1]*m+uvw[:,2]*(np.sqrt(1.-l**2-m**2)-1.)))*Ssel[dd]
                    self.CT.timeit()
                    gains=CIon.GiveGainTEC(dd)
                    Kernel/=gains
                    DataOut[:,spw,0]+=Kernel
                    DataOut[:,spw,3]+=Kernel
        self.DataOut=DataOut



    def SubToCol(self,col="CORRECTED_DATA_BACKUP"):
        self.MS.PutBackupCol(back=col)
        resid=self.MS.GiveCol("%s"%col)-self.DataOut
        self.MS.SaveVis(vis=resid,work_colname=col)

    def WriteInMS(self,col="CORRECTED_DATA",data=None):
        if data==None:
            vis=self.DataOut
        else:
            vis=data
        self.MS.PutBackupCol(back=col)
        self.MS.SaveVis(vis=vis,Col=col)

    
