import numpy as np
from pyrap.tables import table
from ClassMS import ClassMS
from ClassSM import ClassSM
from ClassTimeIt import ClassTimeIt
import numexpr as ne
#import ModNumExpr

class ClassPredict():
    def __init__(self,MS,modelName,Cluster=""):
        if type(MS)==str:
            self.MS=ClassMS(MS,work_colname="CORRECTED_DATA")
        else: 
            self.MS=MS # is a ClassMS!
        self.SM=ClassSM(modelName,infile_cluster=Cluster)
        self.NDir=self.SM.NDir
        self.CT=ClassTimeIt()
        self.NCPU=8
        ne.set_num_threads(self.NCPU)

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

#     def predict(self):
#         SourceCat=self.SM.SourceCat
#         Nchan=self.MS.Nchan
#         uvw=self.MS.uvw
#         DataOut=np.zeros_like(self.MS.data)
#         wave=self.MS.wavelength_chan[0]
#         freq=self.MS.ChanFreq[0]
       
#         for i in range(self.NDir):
#             print "%i/%i"%(i,self.NDir)
#             ind0=np.where(SourceCat.Cluster==i)[0]
#             rasel =SourceCat.ra[ind0]
#             decsel=SourceCat.dec[ind0]
    
#             for spw in range(Nchan):
#                 Ssel  =SourceCat.Sref[ind0]*(freq[spw]/SourceCat.RefFreq[ind0])**(SourceCat.alpha[ind0])
#                 for dd in range(len(ind0)):
#                     l,m=self.MS.radec2lm_scalar(rasel[dd],decsel[dd])
#                     Kernel=np.exp(2*np.pi*1j*(1./wave[spw])*(uvw[:,0]*l+uvw[:,1]*m+uvw[:,2]*(np.sqrt(1.-l**2-m**2)-1.)))*Ssel[dd]
#                     DataOut[:,spw,0]+=Kernel
#                     DataOut[:,spw,3]+=Kernel
# #                    for pol in range(4):
# #                        DataOut[:,spw,pol]+=Kernel
#         self.DataOut=DataOut


    def predict(self):
        SourceCat=self.SM.SourceCat
        Nchan=self.MS.Nchan
        #uvw=self.MS.uvw.copy()
        DataOut=np.zeros_like(self.MS.data)
        freq=self.MS.ChanFreq[0]
        pi=float(np.pi)
        #a = np.random.rand(1e6)+1j*np.random.rand(1e6)
        #ne.evaluate("exp(a)")

        uvwL=self.MS.uvw
        U=uvwL[:,0].astype(float).flatten().copy()
        V=uvwL[:,1].astype(float).flatten().copy()
        W=uvwL[:,2].astype(float).flatten().copy()
       
        for spw in range(Nchan):
            
            wave=self.MS.wavelength_chan.flatten()#[0]
            f0=complex(2*pi*1j/wave[spw])
            ColOut=np.zeros(DataOut[:,0,0].shape,dtype=complex)
            Kernel=np.zeros(DataOut[:,0,0].shape,dtype=complex)

            for i in range(self.NDir):
                print i,"/",self.NDir
                ind0=np.where(SourceCat.Cluster==i)[0]
                rasel =SourceCat.ra[ind0]
                decsel=SourceCat.dec[ind0]
                
                TypeSources=SourceCat.Type[ind0]
                #TypeSources.fill(0)
                Gmaj=SourceCat.Gmaj[ind0]
                Gmin=SourceCat.Gmin[ind0]
                Gangle=SourceCat.Gangle[ind0]
                Ssel  =SourceCat.Sref[ind0]*(freq[spw]/SourceCat.RefFreq[ind0])**(SourceCat.alpha[ind0])
    
                for dd in range(len(ind0)):
                    #if TypeSources[dd]==1: continue
                    l,m=self.MS.radec2lm_scalar(rasel[dd],decsel[dd])
                    l=float(l)
                    m=float(m)
                    nn=float(np.sqrt(1.-l**2-m**2)-1.)

                    #self.CT.reinit()
                    #self.CT.timeit("uvw")
                    f=float(Ssel[dd])
                    #f0=complex(2*pi*1j)

                    KernelPha=ne.evaluate("f0*(U*l+V*m+W*nn)")
                    #self.CT.timeit("kern1")
                    f0b=float(2*pi/wave[spw])
                    #ModNumExpr.EXP_PHAImExpr(Kernel,"f0b*(U*l+V*m+W*nn)",fact=f,f0b=f0b,U=U,V=V,W=W,nn=nn,l=l,m=m)
                    #ModNumExpr.EXP_PHAImExpr(Kernel,"f0b*U",fact=f,f0b=f0b,U=U,V=V,W=W,nn=nn,l=l,m=m)
                    #Kernel=ModNumExpr.EXP_PHAImExpr2("f0b*(U*l+V*m+W*nn)",fact=f,f0b=f0b,U=U,V=V,W=W,nn=nn,l=l,m=m)
                    #self.CT.timeit("kern1")

                    if TypeSources[dd]==1:
                        print "gauss"
                        m1=1./(Gmaj[dd])
                        ang=Gangle[dd]
                        SigMaj=Gmaj[dd]
                        SigMin=Gmin[dd]
                        WaveL=wave[spw]
                        SminCos=SigMin*np.cos(ang)
                        SminSin=SigMin*np.sin(ang)
                        SmajCos=SigMaj*np.cos(ang)
                        SmajSin=SigMaj*np.sin(ang)
                        up=ne.evaluate("U*SminCos-V*SminSin")
                        vp=ne.evaluate("U*SmajSin+V*SmajCos")
                        const=-2*(pi**2)*(1/WaveL)**2
                        uvp=ne.evaluate("const*((U*SminCos-V*SminSin)**2+(U*SmajSin+V*SmajCos)**2)")
                        KernelPha=ne.evaluate("KernelPha+uvp")
                    LogF=np.log(f)
                    Kernel=ne.evaluate("exp(KernelPha+LogF)")
                    ColOut=ne.evaluate("ColOut+Kernel")

            #ColOut*=2.
            DataOut[:,spw,0]+=ColOut
            DataOut[:,spw,3]+=ColOut

        self.DataOut=DataOut

    def PredictDirSPW(self,uvw,idir,spw):
        SourceCat=self.SM.SourceCat
        Nchan=self.MS.Nchan


        freq=self.MS.ChanFreq[0]
        pi=float(np.pi)
        wave=self.MS.wavelength_chan.flatten()#[0]
        f0=complex(2*pi*1j/wave[spw])
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
    
        for dd in range(len(ind0)):
            l,m=self.MS.radec2lm_scalar(rasel[dd],decsel[dd])
            l=float(l)
            m=float(m)
            nn=float(np.sqrt(1.-l**2-m**2)-1.)
            f=float(Ssel[dd])
            
            KernelPha=ne.evaluate("f0*(U*l+V*m+W*nn)")
            f0b=float(2*pi/wave[spw])
            
            if TypeSources[dd]==1:
                print "gauss"
                m1=1./(Gmaj[dd])
                ang=Gangle[dd]
                SigMaj=Gmaj[dd]
                SigMin=Gmin[dd]
                WaveL=wave[spw]
                SminCos=SigMin*np.cos(ang)
                SminSin=SigMin*np.sin(ang)
                SmajCos=SigMaj*np.cos(ang)
                SmajSin=SigMaj*np.sin(ang)
                up=ne.evaluate("U*SminCos-V*SminSin")
                vp=ne.evaluate("U*SmajSin+V*SmajCos")
                const=-2*(pi**2)*(1/WaveL)**2
                uvp=ne.evaluate("const*((U*SminCos-V*SminSin)**2+(U*SmajSin+V*SmajCos)**2)")
                KernelPha=ne.evaluate("KernelPha+uvp")
            LogF=np.log(f)
            Kernel=ne.evaluate("exp(KernelPha+LogF)")
            ColOut=ne.evaluate("ColOut+Kernel")
        return ColOut


    def SubToBackup(self,col="CORRECTED_DATA"):
        self.MS.PutBackupCol(back=col)
        resid=self.MS.GiveCol("%s_BACKUP"%col)-self.DataOut
        self.MS.SaveVis(vis=resid,work_colname=col)



    def WriteInMS(self,col="CORRECTED_DATA",data=None):
        if data==None:
            vis=self.DataOut
        else:
            vis=data
        self.MS.PutBackupCol(back=col)
        self.MS.SaveVis(vis=vis,work_colname=col)

    
