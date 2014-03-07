from widget_mpl_button import Ui_Form
from PyQt4 import QtCore, QtGui
import numpy as np
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

class MplNavigationToolbar(NavigationToolbar):
    '''Class to represent the NavigationToolbar widget'''
    '''Temporarily unecessary until we sort things out'''
    def __init__(self,canvas,parent):
        #NavigationToolbar.__init__(self,parent,canevas)
        #self.layout = QVBoxLayout( self )
        self.canvas = canvas
        #QtGui.QWidget.__init__(self, parent)
        #self.layout.setMargin( 2 )
        #self.layout.setSpacing( 0 )
        NavigationToolbar.__init__(self, canvas, canvas)
        
    def set_message( self, s ):
        pass


import guiLink
class AThread(QtCore.QThread):
    def set(self,ui):
        self.ui=ui

    def start(self):
        self.updateMpl()

    def updateMpl(self):
        self.ui.im.set_clim(self.ui.vmin,self.ui.vmax)
        self.ui.ax.draw_artist(self.ui.im)
        self.ui.fig.canvas.update()
        self.ui.fig.canvas.flush_events()
        self.ui.updateLabels()

from SuperForm import SuperForm

class SuperWidgetButton(SuperForm, Ui_Form):
    def __init__(self):
        SuperForm.__init__(self)
        self.Form = QtGui.QWidget()
        
        Ui_Form.__init__(self)
        self.setupUi(self.Form)
        self.initPlot()
        self.Form.show()

        self.DoLinks()
        self.addToolBar(("verticalLayout_2","mplwidget"))


    def DoLinks(self):
        self.LinkButton("verticalSlider_vmax","updateClimVmax","callSlide")
        self.LinkButton("verticalSlider_vmin","updateClimVmin","callSlide")
        self.LinkButton("doubleSpinBox_vmax","setVMAX","valueChanged(double)")
        self.LinkButton("doubleSpinBox_vmin","setVMIN","valueChanged(double)")

    def LinkButton(self,ButtonField="verticalSlider_vmax",Target="updateClimVmax",Type="callSlide",args=None):
        guiLink.dolink(self,ButtonField,Target,Type,args)

    def updateMplParallel(self):
        thread = AThread()
        thread.set(self)
        thread.start()
        thread.wait()
        thread.terminate()
        del(thread)



    def updateMpl(self):
        print "(%f,%f)"%(self.vmin,self.vmax)
        #self.mplwidget.axes.draw_artist(self.mplwidget.axes.patch)
        self.ax.draw_artist(self.ax.patch)
        
        self.im.set_data(self.data)#self.vmin,self.vmax)
        #self.im.set_clim(self.vmin,self.vmax)
        #self.mplwidget.axes.draw_artist(self.im)
        self.ax.draw_artist(self.im)
        self.fig.canvas.update()
        #self.fig.canvas.flush_events()

    def updateClimVmax(self,val):
        self.vmax=float(val)*self.VMAX/100
        #self.updateMpl()
        self.updateMplParallel()

    def updateClimVmin(self,val):
        self.vmin=float(val)*self.VMIN/100
        #self.updateMpl()
        self.updateMplParallel()


    def updateLabels(self):
        self.label_vmin.setText("%6.2f"%self.vmin)
        self.label_vmax.setText("%6.2f"%self.vmax)
    
    def setVMAX(self,val):
        self.VMAX=self.doubleSpinBox_vmax.value()#getValue()
        self.vmax=self.VMAX
        self.verticalSlider_vmax.setValue(int(100*self.vmax/self.VMAX))
        self.updateMplParallel()

    def setVMIN(self,val):
        self.VMIN=self.doubleSpinBox_vmin.value()#getValue()
        self.vmin=self.VMIN
        self.verticalSlider_vmin.setValue(int(100*self.vmin/self.VMIN))
        self.updateMplParallel()

    def plot(self,data):
        n=data.shape[0]
        
        self.incr=int(n/(self.fig.get_figheight()*600./8))
        self.data=data[::self.incr,::self.incr]
        print self.incr
        self.im.set_data(self.data)
        self.ax.draw_artist(self.im)
        self.fig.canvas.update()
        self.fig.canvas.flush_events()

    # def connect(self,Form):
    #     QtCore.QObject.connect(self.verticalSlider_vmax, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), updateClimVmax)
    #     # #QtCore.QObject.connect(self.verticalSlider_vmin, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.updateClimVmin)
    #     # #QtCore.QObject.connect(self.doubleSpinBox_vmax, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.setVMAX)
    #     # #QtCore.QObject.connect(self.doubleSpinBox_vmin, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.setVMAX)
    #     # QtCore.QMetaObject.connectSlotsByName(Form)

    #     QtCore.QObject.connect(self.verticalSlider_vmax, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.doubleSpinBox_vmax.setValue)
    #     QtCore.QObject.connect(self.verticalSlider_vmax, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.f)
    #     QtCore.QMetaObject.connectSlotsByName(Form)

    
    def initPlot(self):
        self.data=np.random.randn(100,100)
        self.vmin,self.vmax=self.data.min(),self.data.max()

        rect=0,0,1,1
        axisbg="white"
        self.fig=self.mplwidget.figure
        self.mplwidget.axes.set_visible(False)
        self.mplwidget.axes.set_axis_bgcolor("white")

        self.fig.patch.set_facecolor("white")
        self.mplwidget.axes.set_axis_bgcolor(axisbg)
        self.fig.patch.set_facecolor(axisbg)
        self.ax=self.fig.add_axes(rect,axisbg=axisbg)
        self.im=self.ax.imshow(self.data,interpolation="nearest",resample=4)
        #self.im=self.mplwidget.axes.imshow(self.data)
        self.VMIN,self.VMAX=2*self.vmin,2*self.vmax
        self.verticalSlider_vmax.setValue(int(100*self.vmax/self.VMAX))
        self.verticalSlider_vmin.setValue(int(100*self.vmin/self.VMIN))

        self.doubleSpinBox_vmax.setValue(self.VMAX)
        self.doubleSpinBox_vmin.setValue(self.VMIN)
        
        self.im.set_clim(self.VMIN,self.VMAX)
        self.mplwidget.draw()
        self.updateLabels()
    



import StartApp

def test():
    app = StartApp.start()
    Form = QtGui.QWidget()
    ui = SuperWidgetButton()
    #ui.setupUi(Form)
    data=np.random.randn(10,1000,1000)
    #ui.connect(Form)
    Form.show()
    for i in range(10):
        ui.plot(data[i])

    stop
    return Form#sys.exit(app.exec_())
    


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = SuperForm()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

