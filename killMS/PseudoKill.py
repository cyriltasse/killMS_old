import sys
import numpy as np
import numpy.linalg as linalg
import scipy.fftpack as FFT
import scipy.linalg
import time as time_mod
import os
import multiprocessing
import scipy.optimize
import timeit
from progressbar import ProgressBar
from MakeTOP_C import ClassMakeTOP
from ClassModMatOp_C import ClassModMatOp
import ClassTimeIt
import ModColor
#import ModKal
from ClassSols import ClassSols
from pyrap.tables import table
import pylab
   
    
def PseudoKill(PM,delta_time=30,niterin=40,NCPU=6,T0=0,T1=-1,PrintProps=0):
    #import pylab
    global TOP, ModMatOp,niter
    delta_time_bins=int(delta_time*60/PM.MS.dt)
    niter=niterin
    TOP=ClassMakeTOP(PM)
    ModMatOp=ClassModMatOp(PM)

    if PrintProps==0:
        print ModColor.Str(" Solver PROPERTIES: ")
        print "   - Time Step %6.1f min. (%i bins)"%(delta_time,delta_time_bins)
        print "   - Number of CPU = ",NCPU
        print "   - Number of iterations = ",niterin
        print 


    #PM.MS.ReadData(t0=T0,t1=T1)

    ntimes=PM.MS.ntimes
    na=PM.MS.na
    nbl=PM.MS.nbl
    NDir=PM.SM.NDir
    
    time_slots_all=PM.MS.times
    ss=range(0,ntimes,delta_time_bins)
    if ss[-1]!=(ntimes-1): ss.append(ntimes-1)

    #Title="Solving between t=%5.2f and t=%5.2f h"%(T0,T1)
    print ModColor.Str(" Pealing in [%-.2f->%-.2f h]"%(T0,T1),Bold=False)
    toolbar_width = 50
    pBAR= ProgressBar('white', block='=', empty=' ',Title="Solving")
    pBAR.render(0, '%i/%i' % (0,len(ss)-1.))

    #parallel part
    jobs = []
    for itime in range(len(ss)-1): #[0:1]:
        time_value=(time_slots_all[ss[itime]]+time_slots_all[ss[itime+1]])/2.
        Row0=ss[itime]*nbl
        Row1=ss[itime+1]*nbl
        x0=np.ones((NDir*na,),dtype=np.complex) 
        jobs.append([Row0,Row1,x0])

    # ######### DEBUG
    # pylab.ion()
    # xi=1.+(np.random.randn(NDir*na)+1j*np.random.randn(NDir*na))*1e-1
    # #xi.fill(1.)
    # for itime in range(len(ss)-1):
    #     time_value=(time_slots_all[ss[itime]]+time_slots_all[ss[itime+1]])/2.
    #     Row0=ss[itime]*nbl
    #     Row1=ss[itime+1]*nbl
    #     xiout,xi=estimate_xi_pseudo(Row0,Row1)
    #     #xiout,xi=KalmanStep(Row0,Row1,xi)
    # stop
    # ######### DEBUG

    work_queue = multiprocessing.Queue()
    for job in jobs:
        work_queue.put(job)
    result_queue = multiprocessing.Queue()

    workerlist=[]
    for ii in range(NCPU):
        workerlist.append(WorkerSolveStef(work_queue, result_queue))
        workerlist[ii].start()
 
    results = []
    lold=len(results)
    while len(results) < len(jobs):
        result = result_queue.get()
        results.append(result)
        if len(results)>lold:
            lold=len(results)
            pBAR.render(int(100* float(lold) / (len(ss)-1.)), '%i/%i' % (lold,len(ss)-1.))

    for ii in range(NCPU):
        workerlist[ii].shutdown()
        workerlist[ii].terminate()
        workerlist[ii].join()
    
    Sols=ClassSols()
    for ii in range(len(results)):
        iii=ii+1
        xi,row0,row1=results[ii]
        Sols.AppendRawSols(PM.MS.times_all[row0],PM.MS.times_all[row1],xi)

    Sols.FinalizeRawSols(PM.MS.times_all)
    return Sols
    stop

    # G.SolContainer=SolContainer
    # G.AllSolContainer=AllSolContainer

    # ind=SolContainer.itime.argsort()
    # SolContainer=SolContainer[ind]
    # AllSolContainer.SolContainer[AllSolContainerStep]=SolContainer.copy()
    # AllSolContainer.done[AllSolContainerStep]=True
    # AllSolContainerStep+=1
    # np.save("AllSolContainer",AllSolContainer)


def estimate_xi_pseudo(Row0,Row1,xi=None):
    #import pylab
    
    timer=ClassTimeIt.ClassTimeIt()
    timer.reinit()
    Ntimes=(Row1-Row0)/TOP.MS.nbl
    na=TOP.MS.na
    NDir=TOP.SM.NDir


    #A0mat,Amat=TOP.make_A0new(Row0,Row1)
    #timer.timeit(" A0")
    A0matList,AmatList=TOP.make_A0newList(Row0,Row1)
    #timer.timeit(" A0List")
    #timer.timeit(" A0")
    #b=TOP.give_b_P(Row0,Row1)
    # timer.timeit(" b")
    b=TOP.give_b_Pnew(Row0,Row1)
    #timer.timeit(" bp")

    #timer.timeit(" b,P")

    #print na,NDir

    x0=np.ones((na*NDir,),dtype=np.complex)#give_x0(time_value)
    
        
    x0.fill(1.)
    if xi==None:
        xi=x0.copy()
    
    # x0=np.random.randn(na*NDir)+1j*np.random.randn(na*NDir)
    # AmatList=TOP.give_AnewList(x0,A0matList,AmatList,Ntimes)
    # predict0List=ModMatOp.dotAvecList(AmatList,x0.conj(),Ntimes)#np.dot(A,xi.conj())
    # b=predict0List
    # b+=0.1*(np.random.randn(b.size)+1j*np.random.randn(b.size))
    
    
    xbef=np.zeros((niter,xi.shape[0]),dtype=np.complex)

    T_give_Anew=0
    T_give_AHA_flat=0
    T_invertAHAflat=0
    T_dotAHvec=0
    T_dotAvec=0

    #VecWeigth=1./np.sqrt(TOP.weigths)
    xi.fill(1.)
    #xi=1+(np.random.randn(na*NDir)+1j*np.random.randn(na*NDir))
    

    for i in range(niter):
        # #timer.timeit(" borne")
        # timer.reinit()
        # Amat=TOP.give_Anew(xi,A0mat,Amat,Ntimes)
        # AHA=ModMatOp.give_AHA_flat(Amat,Ntimes)
        # AHAinv=ModMatOp.invertAHAflat(AHA,Ntimes)
        # AHvec=ModMatOp.dotAHvec(Amat,b,Ntimes)
        # xi=VecWeigth*ModMatOp.dotAvec(AHAinv,AHvec,Ntimes).conj()
        # timer.timeit(" 11")

        # #print "xi",xi

        AmatList=TOP.give_AnewList(xi,A0matList,AmatList,Ntimes)
        AHAList=ModMatOp.give_AHA_flatList(AmatList,Ntimes)
        AHAinvList=ModMatOp.invertAHAflatList(AHAList,Ntimes)


        # AHvecList=ModMatOp.dotAHvecList(AmatList,b,Ntimes)
        # xi=VecWeigth*ModMatOp.dotAvecList(AHAinvList,AHvecList,Ntimes).conj()

        predict0List=ModMatOp.dotAvecList(AmatList,xi.conj(),Ntimes)#np.dot(A,xi.conj())

        AHvecList=ModMatOp.dotAHvecList(AmatList,b-predict0List,Ntimes)
        xi+=0.5*ModMatOp.dotAvecList(AHAinvList,AHvecList,Ntimes).conj()
        #timer.timeit(" 22")
        #print 
        #xi*=VecWeigth
        



        #=========================================
        xbef[i,:]=xi

        # if (i>1):
        #     xi=(xbef[i-1]+xbef[i])/2.
        #     #print xi

        # #=========================================
        # xip=xi.copy()
        # x0p=x0.copy()

        # for ii in range(NDir):
        #     for ant in range(na):
        #         x0p[ii+ant*NDir]=x0p[ii+ant*NDir]*x0p[ii].conj()/np.abs(x0p[ii])
        #         xip[ii+ant*NDir]=xip[ii+ant*NDir]*xip[ii].conj()/np.abs(xip[ii])

        # pylab.figure(0)
        # pylab.clf()
        # pylab.subplot(2,1,1)
        # pylab.plot(np.abs(x0p),color="black")
        # pylab.plot(np.abs(xip),color="blue")
        # pylab.ylim(0.,5.)
        # x0p,xip=x0.copy(),xi.copy()
        # for ii in range(NDir):
        #     x0p[ii::NDir]*=np.conj(x0p[ii])
        #     xip[ii::NDir]*=np.conj(xip[ii])
        # pylab.subplot(2,1,2)
        # pylab.plot(np.angle(x0p),color="black")
        # pylab.plot(np.angle(xip),color="blue")
        # pylab.plot(np.angle(xip)-np.angle(x0p),color="black",ls="",marker=".")
        # pylab.draw()
        # pylab.show(False)
        # pylab.pause(0.1)

        # #xi.fill(1)
        # #AmatList=TOP.give_AnewList(xi,A0matList,AmatList,Ntimes)
        # AList=TOP.give_AnewList(xi,A0matList,AmatList,Ntimes)
        
        # predict=ModMatOp.dotAvecList(AList,xi.conj(),Ntimes)#np.dot(A,xi.conj())
        # #predict=ModMatOp.dotAvec(A,xi.conj(),Ntimes)
        # pylab.figure(3)
        # pylab.clf()
        # pylab.subplot(2,1,1)
        # n=10
        # # pylab.plot(np.abs(b[::n]),color="black")
        # # pylab.plot(np.abs(predict[::n]),color="green")
        # # pylab.plot(np.abs(b[::n]-predict[::n]),color="red")
        # pylab.plot(b.real[::n],color="black")
        # pylab.plot(predict.real[::n],color="green")
        # pylab.plot(b.real[::n]-predict.real[::n],color="red")
        # pylab.subplot(2,1,2)
        # pylab.plot(b.imag[::n],color="black")
        # pylab.plot(predict.imag[::n],color="green")
        # pylab.plot(b.imag[::n]-predict.imag[::n],color="red")
        # pylab.title("iter=%i"%i)
        # pylab.draw()
        # pylab.show()

        # # # A=give_Anew(xi,A0mat,Amat,Ntimes)
        # # # predict=dotAvec(A,xi.conj(),Ntimes)
        # # # pylab.figure(3)
        # # # pylab.clf()
        # # # pylab.subplot(2,1,1)
        # # # pylab.plot(np.abs(b),color="black")
        # # # pylab.plot(np.abs(predict),color="green")
        # # # pylab.plot(np.abs(predict-b),color="red")
        # # # pylab.subplot(2,1,2)
        # # # pylab.plot(np.angle(b),color="black")
        # # # pylab.plot(np.angle(predict),color="green")
        # # # pylab.draw()
        # # # pylab.show()


    # #timer.timeit(" DONE!!!")
    # # DDX,DDY=mat_pierce(time_value)
    # # Pierce2png(DDX,DDY,xi,itime,"lala",verbose=1)

    xiout=[]
    for idir in range(NDir):
        xiout.append(xi[idir::NDir])
    
    # print TOP.weigths
    # sizeVec=AmatList[0].shape[0]
    # TOP.weigths=np.abs(VecWeigth*ModMatOp.dotAvecList(AHAinvList,TOP.weigths,Ntimes)*sizeVec)
    # print TOP.weigths
    # print "T_give_Anew, T_give_AHA_flat, T_invertAHAflat, T_dotAHvec, T_dotAvec = ",T_give_Anew, T_give_AHA_flat, T_invertAHAflat, T_dotAHvec, T_dotAvec

    # np.savez("xbef",xbef=xbef,x0=x0,NDir=NDir)

    return xiout,xi

# def estimate_xi_pseudo_AllPol(Row0,Row1,time_value,itime,x0,Q=None):
#     Ntimes=(Row1-Row0)/nbl
    
#     A0mat,Amat=make_A0new(Row0,Row1,Ntimes)

#     if x0==None:
#         x0=np.ones((na*NDir,),dtype=np.complex)#give_x0(time_value)
    
        

#     xbef=np.zeros((niter,x0.shape[0],4),dtype=np.complex)
#     for pol in range(4):
#         x0.fill(1.)
#         b,P,maping_row,maping_chan=give_b_P(Row0,Row1,pol=pol)
#         xi=x0.copy()
    
#         for i in range(niter):
#             Amat=give_Anew(xi,A0mat,Amat,Ntimes)
#             AHA=give_AHA_flat(Amat,Ntimes)
#             AHAinv=invertAHAflat(AHA,Ntimes)
#             AHvec=dotAHvec(Amat,b,Ntimes)
#             xi=dotAvec(AHAinv,AHvec,Ntimes).conj()
#             xbef[i,:,pol]=xi
#             if (i>1):
#                 xi=(xbef[i-1,:,pol]+xbef[i,:,pol])/2.

#     return xbef[i,:,:]


class WorkerSolveStef(multiprocessing.Process):
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
            Row0,Row1,x0=job
            #if G.SolvePolMode=="I":
            xi,xii=estimate_xi_pseudo(Row0,Row1)
            # else:
            #     xi=estimate_xi_pseudo_AllPol(Row0,Row1,time_value,itime,x0=x0)
            self.result_queue.put([xi,Row0,Row1])


# class WorkerSolveKalman(multiprocessing.Process):
#     def __init__(self,
#             work_queue,
#             result_queue):
#         multiprocessing.Process.__init__(self)
#         self.work_queue = work_queue
#         self.result_queue = result_queue
#         self.kill_received = False
#         self.exit = multiprocessing.Event()
#     def shutdown(self):
#         self.exit.set()
#     def run(self):
#         while not self.kill_received:
#             try:
#                 job = self.work_queue.get()
#             except:
#                 break
#             ss,itimeVec,worker_show=job

#             if worker_show==1:
#                 print
#                 print "  Solving for the apparant fluxes ..."
#                 toolbar_width = 50#int(len(ss)-1)
#                 pBAR= ProgressBar('white', width=toolbar_width, block='|', empty='.')
#                 pBAR.render(0, 'step %i/%i' % (0,len(ss)-1.))
            
#             xi=np.ones((na*NDir),dtype=np.complex)
            
#             P=np.eye(int(NDir*na),int(NDir*na),dtype=np.complex)*.01
#             F=np.eye(int(NDir*na),int(NDir*na),dtype=np.complex)
#             xbef=np.zeros((len(ss),xi.shape[0]),dtype=np.complex)

#             x_true=np.random.randn(na*NDir)+1j*np.random.randn(na*NDir)
#             time_value=(time_slots_all[ss[0]]+time_slots_all[ss[0+1]])/2.
#             x_true,Jf=smooth(time_value,x_true.copy(),P)
            
#             for itime in range(len(ss)-1):
#                 time_value=(time_slots_all[ss[itime]]+time_slots_all[ss[itime+1]])/2.
#                 Row0=ss[itime]*nbl
#                 Row1=ss[itime+1]*nbl
#                 xi,P,F=estimate_xi(Row0,Row1,time_value,itime,x0=xi,P=P,F=F)#,x_true=x_true)
#                 xbef[itime,:]=xi
#                 if G.doSmooth==True:
#                     xi,F=smooth(time_value,xi.copy(),P)
#                 if worker_show==1:
#                     pBAR.render(int(100* float(itime+1) / (len(ss)-1.)), 'step %i/%i' % (itime+1,len(ss)-1.))



#             self.result_queue.put([ss,xbef,itimeVec])














##### Pierce part


