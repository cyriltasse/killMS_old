import numpy as np
from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
#from gui import Ui_MainWindow as Ui_Form
#from gui import Ui_Form

import guiLink
#import ButtonCorr
import MyPickle
#import SetDico
import ModColor
import StartApp

class SuperForm(QWidget):
    def __init__(self):
        self.app = StartApp.start()
        QWidget.__init__(self)
        #self.FieldCorr=ButtonCorr.giveFieldCorr()
        self.DicoConfig=None
        self.SetDico=None
        self.MS=None
        self.SM=None
        self.C=None
        self.Xp=None

    def setMplWhite(self):
        for at in self.__dict__.keys():
            if "mplwidget" in at:
                print at
                widget=getattr(self,at)
                widget.axes.set_visible(False)
                widget.axes.set_axis_bgcolor("white")
                fig=widget.axes.figure
                fig.clf()
                fig.patch.set_facecolor("white")
                widget.draw()
        

    def addToolBar(self,(LayoutName,mplwidgetName)=("verticalLayout_TECExample","mplwidget_TEC_example")):
        plot_canvas=getattr(self,mplwidgetName)
        plot_layout=getattr(self,LayoutName)
        #plot_canvas=self.mplwidget_TEC_example
        #plot_layout=self.verticalLayout_TECExample
        self.navi_toolbar = NavigationToolbar(plot_canvas, self)
        plot_layout.addWidget(self.navi_toolbar)

    def LinkButton(self,ButtonField="pushButton_FileName",Target="lineEdit_FileName",Type="lineEdit",args=None):
        guiLink.dolink(self,ButtonField,Target,Type,args)

    def GetField(self,FieldName="checkBox_TEC_enable"):
        if not(FieldName in self.__dict__.keys()): return
        This=getattr(self,FieldName)
        ThisType=This.__class__.__name__
        if ThisType=='QCheckBox':
            #print "CheckboxState:",This.isChecked()
            return This.isChecked()
        elif (ThisType=='QSpinBox')|(ThisType=="QDoubleSpinBox"):
            #print ThisType,This.value()
            return This.value()
        elif (ThisType=='QLineEdit'):
            return str(This.text())

    def SetField(self,FieldName="checkBox_TEC_enable",Value=0):
        if not(FieldName in self.__dict__.keys()): return
        This=getattr(self,FieldName)
        ThisType=This.__class__.__name__
        if ThisType=='QCheckBox':
            #print "CheckboxState:",This.isChecked()
            This.setChecked(Value)
        elif (ThisType=='QSpinBox')|(ThisType=="QDoubleSpinBox"):
            #print ThisType,This.value()
            This.setValue(Value)
        elif (ThisType=='QLineEdit'):
            This.setText(str(Value))

    def ToDicoConfig(self):
        FieldCorrList=self.FieldCorr
        DicoConfig={}
        for ThisDico in FieldCorrList:
            FieldName,keys=ThisDico["FieldName"],ThisDico["NameConfig"]
            key0,key1=keys.split(".")
            if not(key0 in DicoConfig.keys()): DicoConfig[key0]={}
            Value=self.GetField(FieldName)
            DicoConfig[key0][key1]=Value
        MyPickle.Save(DicoConfig,"LastDico.pickle")
        setattr(self,"DicoConfig",DicoConfig)


    def FromDicoConfig(self,DicoConfig=None):#):
        if DicoConfig==None:
            print "Must put a dico!!!"
            #return
            File="LastDico.pickle"
            try:
                DicoConfig=MyPickle.Load(File)
            except:
                print "File %s doesn not exist"%File
                return
        setattr(self,"DicoConfig",DicoConfig)
        FieldCorrList=self.FieldCorr

        for ThisDico in FieldCorrList:
            FieldName,keys=ThisDico["FieldName"],ThisDico["NameConfig"]
            key0,key1=keys.split(".")
            if not(key0 in DicoConfig.keys()): continue
            if key1 in DicoConfig[key0].keys():
                Value=DicoConfig[key0][key1]
                self.SetField(FieldName,Value)

    def ConnectAll(self):
        self.ButtonCorrList=ButtonCorr.giveButtonCorr()
        for ThisDico in self.ButtonCorrList:
            FieldName,Target,Type,args=ThisDico["ButtonName"],ThisDico["TargetName"],ThisDico["Type"],ThisDico["args"]
            self.LinkButton(FieldName,Target,Type)


