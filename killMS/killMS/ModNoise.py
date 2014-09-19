import pyfits
import numpy as np
import time
import ModColor

def FindIsland(A,Lpix,x,y,dirfrom=-1,threshold=1):
    T=threshold
    digo=set(range(4))-set([dirfrom])
    #print Lpix
    #time.sleep(1.)
    #if (x,y) in Lpix: return Lpix
    pos=(x,y)
    S=ModColor.Str("@(%i,%i) "%(x,y),col="blue")
    try:
        aa=A[x,y]
    except:
        return


    if A[x,y]==False:
        #print ModColor.Str("(%i,%i)"%(x,y))
        return
    if A[x,y]==True:
        #print S,ModColor.Str("(%i,%i)"%(x,y),col="green")
        Lpix.append((x,y))
    if 0 in digo:
        this=(x+1,y)
        if not(this in Lpix):
            #print S,"-> from %i and going to %i"%(dirfrom,0)
            FindIsland(A,Lpix,x+1,y,dirfrom=2)
    if 2 in digo:
        this=(x-1,y)
        if not(this in Lpix):
            #print S,"-> from %i and going to %i"%(dirfrom,2)
            FindIsland(A,Lpix,x-1,y,dirfrom=0)
    if 1 in digo:
        this=(x,y+1)
        if not(this in Lpix):
            #print S,"-> from %i and going to %i"%(dirfrom,1)
            FindIsland(A,Lpix,x,y+1,dirfrom=3)
    if 3 in digo:
        this=(x,y-1)
        if not(this in Lpix):
            #print "-> from %i and going to %i"%(dirfrom,3)
            FindIsland(A,Lpix,x,y-1,dirfrom=1)

def FindAllIslands(A,T):
    indx,indy=np.where(A>T)
    Lpos=[(indx[i],indy[i]) for i in range(indx.shape[0])]
    LIslands=[]
    Abool=(A>T)
    while True:
        l=[]
        FindIsland(Abool,l,Lpos[0][0],Lpos[0][1])
        LIslands.append(l)
        Lpos=list(set(Lpos)-set(l))
        if len(Lpos)==0: break
    print LIslands


def init():
    a=np.zeros((7,7),dtype=bool)
    a[1:3,3:5]=1
    a[1,5]=1
    a[1,1]=1
    #a[1,2]=1
    print a
    l=[]
    FindIsland(a,l,1,1)
    print l

def init2():
    a=np.zeros((7,7),dtype=bool)
    a[1:3,3:5]=1
    a[1,5]=1
    a[1,1]=1
    a[6,6]=1
    a[5,5]=1
    a[5,6]=1
    #a[1,2]=1
    l=[]
    A=np.zeros((a.shape),dtype=np.float)
    A[a]=10
    print A
    FindAllIslands(A,1.)

