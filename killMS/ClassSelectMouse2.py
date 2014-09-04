import numpy as np
import matplotlib.pyplot as plt
import pylab

class ClassSelectMouse():
    def __init__(self):
        pylab.close(1)
        self.fig = pylab.figure(1)
        self.RectInit=False
        self.IsCliked=False

    def initRect(self):
        self.RectInit=True
        self.rect=self.ax.plot([],[])[0]
        

    def DefineXY(self,(x,y),z=None):
        self.DicoData={}
        self.CurrentSel=0
        self.CatXY=np.zeros((x.shape[0],),dtype=[("x",np.float32),("y",np.float32),("z",np.float32),("sel",np.bool),("FLAG","|S200")])
        self.CatXY=self.CatXY.view(np.recarray)
        self.CatXY.x=x
        self.CatXY.y=y
        if z==None:
            self.CatXY.z=np.ones_like(x)
        else:
            self.CatXY.z=z
        self.CurrentFLAG="FLAG"

    def UpdateXY(self):
        self.line=self.ax.scatter(self.CatXY.x,self.CatXY.y,s=(self.CatXY.z-np.min(self.CatXY.z))*10)
        for group in self.DicoData.keys():
            xa,ya=self.DicoData[group][0]
            xb,yb=self.DicoData[group][1]
            x0,x1=np.min([xa,xb]),np.max([xa,xb])
            y0,y1=np.min([ya,yb]),np.max([ya,yb])
            condx=(self.CatXY.x>x0)&(self.CatXY.x<x1)
            condy=(self.CatXY.y>y0)&(self.CatXY.y<y1)
            ind=np.where(condx&condy)[0]
            self.CatXY.sel[ind]=True
            self.CatXY.FLAG[ind]=self.CurrentFLAG

        ind=np.where(self.CatXY.sel==True)[0]
        self.ax.scatter(self.CatXY.x[ind],self.CatXY.y[ind],color="red")
        pylab.draw()

    def Start(self):
        pylab.clf()
        pylab.cla()
        self.ax = pylab.subplot(111)
        self.UpdateXY()
        self.initRect()
        self.updateTitle()
        self.cid=[]
        self.cid.append( self.fig.canvas.mpl_connect('button_press_event', self.onclick))
        self.cid.append( self.fig.canvas.mpl_connect('button_release_event', self.outclick))
        self.cid.append( self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion))
        #self.cid = self.fig.canvas.mpl_connect('key_press_event', self.keypress)
        pylab.draw()
        pylab.show()
        self.Stop()
        return self.CatXY.sel

    def Stop(self):
        for cid in self.cid:
            self.fig.canvas.mpl_disconnect(cid)

    def updateTitle(self):
        self.ax.set_title("Current flag: %s"%self.CurrentFLAG)

    def keypress(self,event):
        if event.key in ["c"]:
            self.CurrentFLAG  = raw_input("New FLAG: ")
            self.updateTitle()
            self.fig.canvas.draw()

        

    def onclick(self,event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #    event.button, event.x, event.y, event.xdata, event.ydata)
        if event.button==3: pylab.close(1)
        self.DicoData[self.CurrentSel]={}
        self.DicoData[self.CurrentSel][0]=(event.xdata, event.ydata)
        self.OnX=event.xdata
        self.OnY=event.ydata
        self.IsCliked=True


    def on_motion(self, event):
        #'on motion we will move the rect if the mouse is over us'
        #if self.press is None: return
        #if event.inaxes != self.rect.axes: return
        #x0, y0, xpress, ypress = self.press
        #dx = event.xdata - xpress
        #dy = event.ydata - ypress
        #print 'x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f'%(x0, xpress, event.xdata, dx, x0+dx)
        if self.IsCliked==False: return
        self.rect.set_xdata([self.OnX,   self.OnX,event.xdata,event.xdata,self.OnX])
        self.rect.set_ydata([self.OnY,event.ydata,event.ydata,   self.OnY,self.OnY])
        self.fig.canvas.draw()

    def outclick(self,event):
        self.DicoData[self.CurrentSel][1]=(event.xdata, event.ydata)
        self.CurrentSel+=1
        self.UpdateXY()
        self.IsCliked=False
        self.rect.set_xdata([])
        self.rect.set_ydata([])
        self.fig.canvas.draw()
#        print self.DicoData

if __name__=="__main__":
    a=ClassSelectMouse()
    x = np.arange(100)/(99.0)
    y = np.sin(x)
    a.DefineXY((x,y))
    a.Start()
