#!/usr/bin/env python


import ModParsetType
import ClassMS
import os
import numpy as np
import ephem

def GiveDate(tt):
    import pyrap.quanta as qa
    import pyrap.measures as pm
    time_start = qa.quantity(tt, 's')
    me = pm.measures()
    dict_time_start_MDJ = me.epoch('utc', time_start)
    time_start_MDJ=dict_time_start_MDJ['m0']['value']
    JD=time_start_MDJ+2400000.5-2415020
    d=ephem.Date(JD)

    return d.datetime().isoformat().replace("T","/")

class Conform():
    def __init__(self,MSname,SPW):

    #MS=ClassMS.ClassMS("/media/6B5E-87D0/TestOlegVLA/3C147_nobl_spw2.MS",Col="CORRECTED_DATA")
        self.Cols=["DATA","CORRECTED_DATA"]
        print SPW
        self.MS=ClassMS.ClassMS(MSname,Col=self.Cols,SelectSPW=SPW)
        print "done read"
        #self.MS1name=self.MS.MSName+".reformed_p0"
        self.MS1name=self.MS.MSName+".reformed"
        self.RevertFreqs=False
        if self.MS.dFreq<0:
            self.RevertFreqs=True
        #self.RevertFreqs=True

        time1=self.MS.times_all
        print "sort"
        list_t1=sorted(list(set(time1.tolist())))
        print "done sort"
        t1=np.array(list_t1)
        dt1=t1[1::]-t1[0:-1]
        self.Dt=np.median(dt1)
        

    

    def makems(self):
        D={}
        MS=self.MS
        MS1name=self.MS1name
        
        DateTime=GiveDate(np.min(MS.times_all))
        # Date,Time=DateTime.datetime().date().isoformat(),DateTime.datetime().time().isoformat()
        # SDateTime=Date+'/'+Time

        D["AntennaTableName"]={"id":0,"val":MS.MSName+"/ANTENNA"}
        D["Declination"]={"id":0,"val":MS.StrDEC}
        D["RightAscension"]={"id":0,"val":MS.StrRA}
        D["MSName"]={"id":0,"val":MS1name}
        D["WriteAutoCorr"]={"id":0,"val":MS.MSName+".reformed"}
        D["NFrequencies"]={"id":0,"val":MS.Nchan}
        D["StepTime"]={"id":0,"val":self.Dt}#MS.dt}
        D["NBands"]={"id":0,"val":1}
        D["WriteAutoCorr"]={"id":0,"val":"T"}
        D["StepFreq"]={"id":0,"val":np.abs(MS.dFreq)}

        D["StartFreq"]={"id":0,"val":np.min(MS.ChanFreq.flatten())-np.abs(MS.dFreq)/2.}
        #D["StartFreq"]={"id":0,"val":np.min(MS.ChanFreq.flatten())}
        D["StartTime"]={"id":0,"val":DateTime}#"29-sep-2005/13:00:00"}
        D["NTimes"]={"id":0,"val":int((np.max(MS.times_all)-np.min(MS.times_all))/self.Dt)+3}
        #D["NParts"]={"id":0,"val":1}

        D["VDSPath"]={"id":0,"val":"."}
        D["WriteImagerColumns"]={"id":0,"val":"T"}
    
        ModParsetType.DictToParset(D,"makems.tmp.cfg")
        os.system("cat makems.tmp.cfg")
        #os.system("makems makems.tmp.cfg")
        ss="/home/cyril/build/awimager/build/gnu_opt/CEP/MS/src/makems makems.tmp.cfg"
        print ss
        os.system(ss)



    def putInMS(self):
        MS=self.MS
        MS1name=self.MS1name
        
        from pyrap.tables import table
        MSout=ClassMS.ClassMS(MS1name,Col=self.Cols)
        
        idx=0
        AntMap=np.zeros((MS.na,MS.na),dtype=np.int32)
        for i in range(MS.na):
            for j in range(i,MS.na):
                #AntMap[i,j]=idx
                AntMap[MSout.A0[idx],MSout.A1[idx]]=idx
                idx+=1

        t0=MS.times_all[0]
        it=np.int64(np.round((MS.times_all-t0)/self.Dt))*MSout.nbl
        Rowmap=it+AntMap[MS.A0,MS.A1]
        
        indIn=np.arange(MS.uvw.shape[0])
        MSout.flag_all.fill(1)
        
        #replace:
        MSout.uvw[Rowmap,:]=MS.uvw[:,:]
        #MSout.times_all[Rowmap]=MS.times_all[:]
        MSout.A0[Rowmap]=MS.A0[:]
        MSout.A1[Rowmap]=MS.A1[:]
        
        if not(self.RevertFreqs):
            for i in range(len(self.Cols)):
                MSout.data[i][Rowmap,:,:]=MS.data[i][:,:,:]
            MSout.flag_all[Rowmap,:,:]=MS.flag_all[:,:,:]
        else:
            for i in range(len(self.Cols)):
                MSout.data[i][Rowmap,::-1,:]=MS.data[i][:,:,:]
            MSout.flag_all[Rowmap,::-1,:]=MS.flag_all[:,:,:]

        MSout.SaveAllDataStruct()

        t=table(MS.MSName+"::SPECTRAL_WINDOW",ack=False,readonly=False)
        chanFreqs=t.getcol('CHAN_FREQ')
        chanWidth=t.getcol('CHAN_WIDTH')
        t.close()
        for spw in range(chanFreqs.shape[0]):
            ind=np.argsort(chanFreqs[spw])
            chanFreqs[spw][:]=chanFreqs[spw][ind]
            chanWidth[spw][:]=np.abs(chanWidth[spw][ind])

        t=table(MSout.MSName+"::SPECTRAL_WINDOW",ack=False,readonly=False)
        t.putcol('CHAN_FREQ',chanFreqs)
        t.putcol('CHAN_WIDTH',chanWidth)
        t.close()



def test():
    
    import sys
    MSname="1365275227_TriAust"#sys.argv[1]
    C=Conform(MSname,None)
    C.makems()
    C.putInMS()




if __name__=="__main__":
    import sys
    MSname=sys.argv[1]
    SPW=None
    print sys.argv
    if len(sys.argv)==3:
        SPW=[int(sys.argv[2])]

    print 
    C=Conform(MSname,SPW)
    C.makems()
    C.putInMS()

