import sys                                         
import pylab                                       
import numpy as np                                 
import numpy.linalg as linalg                      
import scipy.fftpack as FFT                        
import time as time_mod                            
import os                                          
import scipy.optimize                              
import timeit                                      
import ClassTimeIt

class ClassModMatOp():
    def __init__(self,PM):
        self.na=PM.MS.na
        self.nbl=PM.MS.nbl
        self.NSPWChan=PM.MS.NSPWChan
        self.NDir=PM.SM.NDir

    def invertAHAflat(self,AHA,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=AHA[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            AHA[:,jblock:jblock+NDir]=linalg.inv(subMat)
        return AHA
        
    def invertAHAflatList(self,AHAList,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=AHAList[i]
            AHAList[i]=linalg.inv(subMat)
        return AHAList
        
    def invertAHAflatDiag(self,AHA,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        NrowBlock=Ntimes*NSPWChan*na
        AHAinv=np.zeros(AHA.shape,dtype=AHA.dtype)
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat    = AHA[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            subMatInv = AHAinv[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            SdKeep=AHA.strides
            subMat.strides=(subMat.strides[1]+subMat.strides[0],subMat.strides[0])
            SdKeepInv=AHAinv.strides
            subMatInv.strides=(subMatInv.strides[1]+subMatInv.strides[0],subMatInv.strides[0])
            subMatInv[:,0]=1./subMat[:,0]
            subMatInv.strides=SdKeepInv; subMat.strides=SdKeep
        return AHAinv




    def give_AHA_flat(self,A,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        AHA=np.zeros((NDir,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        #timer=ClassTimeIt.ClassTimeIt()
        #a=np.zeros((52894, 30),dtype=np.complex128)+np.random.rand(52894, 30)+1j*np.random.rand(52894, 30)
        
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=A[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            #timer.timeit("select")
            #AHA[:,jblock:jblock+NDir]=np.dot((subMat.T.conj()).copy(),subMat.copy())
            AHA[:,jblock:jblock+NDir]=np.dot(subMat.T.conj(),subMat)
            #timer.timeit("dot1 dim=%s dtype=%s strides=%s"%(str(subMat.shape),str(subMat.dtype),str(subMat.strides)))
            # b=np.dot(a.T.conj(),a)
            # timer.timeit("dot2 dim=%s dtype=%s strides=%s"%(str(a.shape),str(a.dtype),str(a.strides)))

        #print "AHA.shape[0]",AHA.shape[0]
        for ant in range(na):
            for i in range(AHA.shape[0]):
                if AHA[i,i+ant*NDir]==0.:
                    AHA[i,i+ant*NDir]=1.e-6
        #timer.timeit("ZEROING")
        #print 
        #print 
        return AHA

    def GiveS(self,P,Amat):
        S=[]
        na=self.na
        NDir=self.NDir
        rmat=np.random.rand(Amat[0].shape[0],Amat[0].shape[0])*1e3
        for i in range(len(Amat)):
            mat=Amat[i]
            p=np.diag(P[i])
            #prod=np.dot(mat,p.reshape(NDir,1)*mat.T.conj())
            prod=np.dot(mat,mat.T.conj())
            ind=(np.abs(prod)<1e3)
            prod[ind]=rmat[ind]
            S.append(prod)
        return S

    def InvMatList(self,A):
        Ainv=[]
        for i in range(len(A)):
            mat=A[i]
            Ainv.append(linalg.inv(mat))
        return Ainv

    def ListToArray(self,MatL):
        S=MatL[0].shape
        dx,dy=S
        out=np.zeros((S[0]*len(MatL),S[1]*len(MatL)),MatL[0].dtype)
        for i in range(len(MatL)):
            out[i*dx:(i+1)*dx,i*dy:(i+1)*dy]=MatL[i]
        return out
        


    def ProdList(self,A,B,Ah=False,Bh=False):
        Out=[]
        for i in range(len(A)):
            if Ah:
                x=A[i].T.conj()
            else:
                x=A[i]
            if Bh:
                y=B[i].T.conj()
            else:
                y=B[i]
            Out.append(np.dot(x,y))
        return Out

    
    def give_AHA_flatList(self,A,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        #AHA=np.zeros((NDir,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        AHAList=[]
        timer=ClassTimeIt.ClassTimeIt()
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=A[i]
            #timer.timeit("select List")
            #AHA[:,jblock:jblock+NDir]=np.dot((subMat.T.conj()).copy(),subMat.copy())
            AHAList.append(np.dot(subMat.T.conj(),subMat))
            #timer.timeit("dot List dim=%s"%str(subMat.shape))
        # for ant in range(na):
        #     for i in range(AHA.shape[0]):
        #         if AHAList[i,i+ant*NDir]==0.:
        #             AHAList[i,i+ant*NDir]=1.e-6
        return AHAList
    
    def give_AHA_flatCopy(self,A,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        AHA=np.zeros((NDir,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        ATc=A.T.conj().copy()
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=A[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            subMatTc=ATc[jblock:jblock+NDir,iblock:iblock+NrowBlock]
            AHA[:,jblock:jblock+NDir]=np.dot(subMatTc,subMat)
        


        # for ant in range(na):
        #     for i in range(AHA.shape[0]):
        #         if AHA[i,i+ant*NDir]==0.:
        #             AHA[i,i+ant*NDir]=1.e-6
        
        return AHA
    
    def give_AHA(self,A,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        AHA=np.zeros((NDir*na,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=A[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            AHA[jblock:jblock+NDir,jblock:jblock+NDir]=np.dot(subMat.T.conj(),subMat)
        for i in range(AHA.shape[0]):
            if AHA[i,i]==0.:
                AHA[i,i]=1.e-6
        
        return AHA
    
    def give_AHA_P(self,A,Ntimes,P):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        AHA=np.zeros((NDir*na,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=0
            jblock=i*NDir
            subMat=A[iblock:iblock+NrowBlock,jblock:jblock+NDir]
            AHA[jblock:jblock+NDir,jblock:jblock+NDir]=np.dot(subMat.T.conj(),subMat)*P
        for i in range(AHA.shape[0]):
            if AHA[i,i]==0.:
                AHA[i,i]=1.e-6
        
        return AHA
    
    
    def dotAHvec(self,A,vec,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        dotAHvec=np.zeros((NDir*na,),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=i*Ntimes*NSPWChan*na
            jblock=i*NDir
            subMat=A[0:NrowBlock,jblock:jblock+NDir]
            dotAHvec[jblock:jblock+NDir]=np.dot((subMat.T).conj(),vec[iblock:iblock+NrowBlock])
        return dotAHvec
    
    def dotAHvecList(self,AList,vec,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        dotAHvec=np.zeros((NDir*na,),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            iblock=i*Ntimes*NSPWChan*na
            jblock=i*NDir
            subMat=AList[i]
            dotAHvec[jblock:jblock+NDir]=np.dot((subMat.T).conj(),vec[iblock:iblock+NrowBlock])
        return dotAHvec
    
    def dotAvec(self,A,vec,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        #print "A",A.shape
        dotAHvec=np.zeros((A.shape[0]*na,),dtype=np.complex)
        NrowBlock=A.shape[0]#Ntimes*NSPWChan*na
        for i in range(na):
            iblock=i*A.shape[0]#Ntimes*NSPWChan*na
            jblock=i*NDir
            subMat=A[0:NrowBlock,jblock:jblock+NDir]
            dotAHvec[iblock:iblock+NrowBlock]=np.dot(subMat,vec[jblock:jblock+NDir])
        return dotAHvec
    
    def dotAvecList(self,AList,vec,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        length=AList[0].shape[0]
        dotAHvec=np.zeros((length*na,),dtype=np.complex)
        NrowBlock=length
        for i in range(na):
            iblock=i*length
            jblock=i*NDir
            subMat=AList[i]
            dotAHvec[iblock:iblock+NrowBlock]=np.dot(subMat,vec[jblock:jblock+NDir])
        return dotAHvec
    
    def putAbig(self,Ain,Ntimes):
        Aret=np.zeros((NSPWChan*Ntimes*na*na,NDir*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        for i in range(na):
            icoord=i*Ntimes*NSPWChan*na
            jcoord=i*NDir
            Aret[icoord:icoord+NrowBlock,jcoord:jcoord+NDir]=Ain[0:NrowBlock,jcoord:jcoord+NDir]
        return Aret
    
    def putAHAbig(self,Ain,Ntimes):
        na=self.na
        NDir=self.NDir
        NSPWChan=self.NSPWChan
        Aret=np.zeros((NDir*na,NDir*na),dtype=np.complex)
        NrowBlock=NDir
        for i in range(na):
            icoord=i*NDir
            jcoord=i*NDir
            Aret[icoord:icoord+NrowBlock,jcoord:jcoord+NrowBlock]=Ain[0:NrowBlock,jcoord:jcoord+NrowBlock]
        return Aret
    
    def dotDiagMDiagH(self,diag0,Mat,diag1):
        #diag0 and diag1 and diagonal matrices given as vectors
        #compute diag0.Mat.diag1^H
    
        for i in range(Mat.shape[0]):
            Mat[:,i]*=diag1[i].conj()
        for i in range(Mat.shape[0]):
            Mat[i,:]*=diag0[i]
    
        return Mat
    
        
    def dotAPAh(self,A,P,Ntimes):
        dotAPAh=np.zeros((NSPWChan*Ntimes*na*na,NSPWChan*Ntimes*na*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        BlockSizeOut=Ntimes*NSPWChan*na
        for i in range(na):
            for j in range(na):
                iblockP=i*NDir
                jblockP=j*NDir
                jblockA1=j*NDir
                jblockA0=i*NDir
                iblockOut=i*BlockSizeOut
                jblockOut=j*BlockSizeOut
                subMat0=A[0:NrowBlock,jblockA0:jblockA0+NDir]
                subMat1=A[0:NrowBlock,jblockA1:jblockA1+NDir]
                Psel=P[iblockP:iblockP+NDir,jblockP:jblockP+NDir]
                dotAPAh[iblockOut:iblockOut+BlockSizeOut,jblockOut:jblockOut+BlockSizeOut]=np.dot(np.dot(subMat0,Psel),subMat1.T.conj())
        # ind=np.where(dotAPAh==0.)
        # rr=(np.random.randn(dotAPAh.shape[0],dotAPAh.shape[0])+1j*np.random.randn(dotAPAh.shape[0],dotAPAh.shape[0]))*1.e-6
        # dotAPAh[ind]=rr[ind]
        for i in range(dotAPAh.shape[0]):
            if dotAPAh[i,i]==0.:
                dotAPAh[i,i]=np.random.rand(1)[0]*1.e-6
        return dotAPAh
    
    def dotAhMat(self,A,Mat,Ntimes):
        dotAhMat=np.zeros((na*NDir,NSPWChan*Ntimes*na*na),dtype=np.complex)
        NrowBlock=Ntimes*NSPWChan*na
        BlockSizeOut=Ntimes*NSPWChan
        for i in range(na):
            jblockA=i*NDir
            subMat0=A[0:NrowBlock,jblockA:jblockA+NDir]
    
            iblockMat=i*Ntimes*NSPWChan*na
            MatSel=Mat[iblockMat:iblockMat+NrowBlock,:]
            iblockOut=i*NDir
            #print i, iblockOut,iblockOut+NDir,iblockMat,iblockMat+NrowBlock
            dotAhMat[iblockOut:iblockOut+NDir,:]=np.dot(subMat0.T.conj(),MatSel)
        return dotAhMat
    
    # def dotMatA(Mat,A,Ntimes):
    #     dotAhMat=np.zeros((na*NDir,na*NDir),dtype=np.complex)
    #     NrowBlock=Ntimes*NSPWChan*na
    #     BlockSizeOut=Ntimes*NSPWChan
    #     for i in range(na):
    #         jblockA=i*NDir
    #         subMat0=A[0:NrowBlock,jblockA:jblockA+NDir]
    
    #         iblockMat=i*Ntimes*NSPWChan*na
    #         MatSel=Mat[iblockMat:iblockMat+NrowBlock,:]
    #         iblockOut=i*NDir
    #         print i, iblockOut,iblockOut+NDir,iblockMat,iblockMat+NrowBlock
    #         dotAhMat[iblockOut:iblockOut+NDir,:]=np.dot(subMat0.T.conj(),MatSel)
    #     return dotAhMat
    
