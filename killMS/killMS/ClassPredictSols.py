
import sys
import pylab
import numpy as np
import numpy.linalg as linalg
import scipy.fftpack as FFT
import time as time_mod
import os
import multiprocessing
import timeit
from progressbar import ProgressBar
from pyrap.tables import table
import ClassPredict


class ClassPredictSols(ClassPredict.ClassPredict):
    def __init__(self,MS,modelName,Cluster="",NCPU=None):
        ClassPredict.ClassPredict.__init__(self,MS,modelName,Cluster)
        if NCPU==None:
            self.NCPU=multiprocessing.cpu_count()-2
            print "using ",self.NCPU
        ClassPredict.ne.set_num_threads(1)
        
        
    def predict_parallel(self,Sols=None):
        

        ChunkSize=int(self.MS.ntimes/self.NCPU)
        jobs=[]
        ss=range(0,self.MS.nrows,ChunkSize*self.MS.nbl)
        if ss[-1]!=self.MS.nrows-1: ss.append(self.MS.nrows-1)

        for ii in range(len(ss)-1):
            row0=ss[ii]
            row1=ss[ii+1]
            
            jobs.append([row0,row1,Sols,self])
    
        work_queue = multiprocessing.Queue()
        for job in jobs:
            work_queue.put(job)
        result_queue = multiprocessing.Queue()
    
        workerlist=[]
        
        for ii in range(self.NCPU):
            #print "start worker ",ii 
            workerlist.append(WorkerSub2Vis(work_queue, result_queue))
            workerlist[ii].start()
    
        results = []
        lold=len(results)
        while len(results) < len(jobs):
            result = result_queue.get()
            results.append(result)
            # if len(results)>lold:
            #     lold=len(results)
            #     pBAR.render(int(100* float(lold) / (Ntot)), 'step %i/%i' % (lold,Ntot))
    
        vis=np.zeros_like(self.MS.data)
        for rr in range(len(results)):
            vbuf,row0,row1=results[rr]
            vis[:,row0:row1,:]=vbuf
    
        for ii in range(self.NCPU):
            workerlist[ii].shutdown()
            workerlist[ii].terminate()
            workerlist[ii].join()
        
    
   
class WorkerSub2Vis(multiprocessing.Process):
    def __init__(self,
            work_queue,
            result_queue):
        multiprocessing.Process.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False
        self.exit = multiprocessing.Event()
    def shutdown(self):
        self.exit.set()
    def run(self):
        while not self.kill_received:
            try:
                job = self.work_queue.get()
            except:
                break
            row0,row1,Sols,PM=job
            vbufin=PM.predict(Sols=Sols,pBAR=False,SetAsAttribute=False,Row01=(row0,row1))
            self.result_queue.put([vbufin,row0,row1])
    
    
    
