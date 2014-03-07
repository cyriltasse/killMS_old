
import pylab


class MyPyplot():
    def __init__(self,nx,ny,fig=1):
        self.fig=pylab.figure(1)
        self.fig.clf()
        self.DoPlot=True

    def subplot(self,nx,ny,n):
        if not(self.DoPlot): return
        self.ax=pylab.subplot(nx,ny,n)

    def imshow(self,im,draw=True,**kwargs):
        if not(self.DoPlot): return
        self.ax.imshow(im,**kwargs)
        if draw:
            pylab.draw()
            pylab.pause(0.01)

    def show(self,block=False):
        if not(self.DoPlot): return
        pylab.show(block)
