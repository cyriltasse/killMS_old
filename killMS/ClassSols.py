import numpy as np
import scipy.ndimage


class ClassSols():
    def __init__(self,ClockTECfileIn=None,BPFileIn=None,PredictMachine=None):#"AmplitudeFits.npz"):
        #ClockTECfileIn="clocktec.xmmlss.send.npy.npz"
        
        self.TimeRawSolStart=[]
        self.TimeRawSolEnd=[]
        self.RawSol=[]

        if BPFileIn!=None:
            BPfile=np.load(BPFileIn)
            self.BPTimes=BPfile["times"]
            self.BPCoefs=BPfile["sols"]
            self.ntimes=self.BPCoefs.shape[0]

        if ClockTECfileIn!=None:
            ClockTECfile=np.load(ClockTECfileIn)
            self.ClockTimes=ClockTECfile["times"]
            Clock=ClockTECfile["clock"]#scipy.ndimage.filters.uniform_filter(ClockTECfile["clock"]*1e-9,size=(100,1))
            OffSet=ClockTECfile["offset"]#scipy.ndimage.filters.uniform_filter(ClockTECfile["offset"],size=(100,1))
            self.Phases=(ClockTECfile["phases"][:,:,:,0,0]+ClockTECfile["phases"][:,:,:,0,1])/2.
            TEC=ClockTECfile["tec"]
            self.freqs=ClockTECfile["freqs"]
            self.na=TEC.shape[1]
            for i in range(self.na):
                Clock[:,i]-=Clock[:,2]
                OffSet[:,i]-=OffSet[:,2]
                TEC[:,i]-=TEC[:,2]
                self.Phases[:,:,i]-=self.Phases[:,:,2]
            self.Clock=Clock
            self.TEC=TEC
            self.OffSet=OffSet
            self.K=8.4479745e9
            if "radeccal" in ClockTECfile.keys():
                self.RaCal=ClockTECfile["radeccal"][:,0]
                self.DecCal=ClockTECfile["radeccal"][:,1]
            else:
                self.RaCal=[ClockTECfile["radec"][0]]
                self.DecCal=[ClockTECfile["radec"][1]]
            print "  ClassSols: %i ant, TEShape %s"%(self.na,str(self.TEC.shape)) 

    def AppendRawSols(self,TimeStart,TimeEnd,Sol):
        self.TimeRawSolStart.append(TimeStart)
        self.TimeRawSolEnd.append(TimeEnd)
        self.RawSol.append(Sol)

    def FinalizeRawSols(self,Tvec):
        SolArray=np.array(self.RawSol)
        SolIndex=np.zeros(Tvec.shape,dtype=int)
        for i in range(len(self.RawSol)):
            SolIndex[(Tvec>self.TimeRawSolStart[i])&(Tvec<self.TimeRawSolEnd[i])]=i
        self.SolArray=SolArray
        self.SolIndex=SolIndex
        

    def GiveRawSols(self,Tvec,A0Vec,A1Vec,spw=None,idir=0):
        
        # times=Tvec
        # DtTEC=(np.max(self.SolsTimes)-np.min(self.SolsTimes))/self.SolsTimes.shape[0]
        # tbinClock=((times-np.min(times))/DtTEC).astype(np.int64)
        # tbinClock[tbinClock>=self.SolsTimes.shape[0]]=self.SolsTimes.shape[0]-1
        # Freq=MS.reffreq
        # TECmat=CIon.TEC[:,dirin,:]-CIon.TECc[:,0,:]
        # dTEC=TECmat[tbinClock,MS.A0]-TECmat[tbinClock,MS.A1]
        # return np.exp(1j*self.K*dTEC/freq)
        
        GainProd=self.SolArray[self.SolIndex,idir,A0Vec]*(self.SolArray[self.SolIndex,idir,A1Vec].conj())
        return GainProd



    def GiveTEC(self,time):
        return self.TEC[np.argmin(np.abs(time-self.ClockTimes))]

    def GiveGainsBP(self,freq):
        gainBP=np.zeros((self.ntimes,self.na),dtype=np.float32)
        for i in range(self.ntimes):
            for j in range(self.na):
                P = np.poly1d(self.BPCoefs[i,j])
                gainBP[i,j]=P(freq)
        return gainBP


    # def DefSolsFreq(self,freq):
    #     self.Gain=self.GiveGainsBP(freq)*self.GiveGainsClockOff(freq)
    #     return self.Gain

    def DefSolsFreqBP(self,freq):
        self.GainBP=self.GiveGainsBP(freq)
        return self.GainBP

    def DefSolsFreqClock(self,freq,ant=None,time=None):
        if ant==None:
            self.GainClock= np.exp(1j*(2.*np.pi*freq*self.Clock*1e-9+self.OffSet))
        else:
            self.GainClock= np.exp(1j*(2.*np.pi*freq*self.Clock[time,ant]*1e-9+self.OffSet[time,ant]))
        return self.GainClock

    def DefSolsTEC(self,freq,ant=None,time=None):
        if ant==None:
            self.GainTEC=np.exp(1j*self.K*self.TEC/freq)
        else:
            self.GainTEC=np.exp(1j*self.K*self.TEC[time,ant]/freq)
            print "tec:",self.TEC[time,ant]
        return self.GainTEC

    def DefSolsClockTEC(self,freq):
        self.GainTEC=np.exp(1j*(self.K*self.TEC/freq+2.*np.pi*freq*self.Clock*1e-9+self.OffSet))
        return self.GainTEC

    def ClockTECfunc(self,freq,par):
        print par
        xarray=freq
        delay=par[1]*1e-9 #in ns
        delayfact=2*np.pi*xarray*delay
        TEC=par[0];
        drefract=8.4479745e9*TEC/xarray;
        return drefract+delayfact+par[2];
