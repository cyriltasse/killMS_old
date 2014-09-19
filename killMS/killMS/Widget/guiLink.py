from PyQt4 import QtCore, QtGui
_fromUtf8 = QtCore.QString.fromUtf8
import ModColor

class LinkClass():
    def __init__(self,ui):
        self.ui=ui

    def selectFile(self):
            lineEdit=getattr(self.ui,self.NameField)
            lineEdit.setText(QtGui.QFileDialog.getOpenFileName())



    def link(self,ButtonField="pushButton_FileName",Target="lineEdit_FileName",Type="lineEdit"):
        self.ButtonField=ButtonField
        if Type=="lineEdit":
            self.NameField=Target
            print "%s -> %s [lineEdit]"%(self.ButtonField,self.NameField),

            if self.ButtonField in self.ui.__dict__.keys():
                print ModColor.Str("Do connect","green")
                Button=getattr(self.ui,self.ButtonField)
                Button.clicked.connect(self.selectFile)
            else:
                print ModColor.Str("Not connect")
        elif Type=="call":
            print "%s -> %s"%(self.ButtonField, Target),
            if self.ButtonField in self.ui.__dict__.keys():
                print ModColor.Str("Do connect","green")
                Button=getattr(self.ui,self.ButtonField)
                ListObj=Target.split(".")
                ThisTarget=getattr(self.ui,ListObj[0])
            # for i in range(1,len(ListObj)):
            #     if ListObj[i] in self.__dict__.keys():
            #         ThisTarget=getattr(ThisTarget,ListObj[i])
                print self.ButtonField, ThisTarget
                QtCore.QObject.connect(Button, QtCore.SIGNAL(_fromUtf8("pressed()")), ThisTarget)
            else:
                print ModColor.Str("Not connect")
        elif Type=="callSlide":
            print "%s -> %s"%(self.ButtonField, Target),
            if self.ButtonField in self.ui.__dict__.keys():
                print ModColor.Str("Do connect","green")
                Button=getattr(self.ui,self.ButtonField)
                ListObj=Target.split(".")
                ThisTarget=getattr(self.ui,ListObj[0])
            # for i in range(1,len(ListObj)):
            #     if ListObj[i] in self.__dict__.keys():
            #         ThisTarget=getattr(ThisTarget,ListObj[i])
                print self.ButtonField, ThisTarget
                QtCore.QObject.connect(Button, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), ThisTarget)
            else:
                print ModColor.Str("Not connect")
        else:
            print "%s -> %s"%(self.ButtonField, Target),
            if self.ButtonField in self.ui.__dict__.keys():
                print ModColor.Str("Do connect","green")
                Button=getattr(self.ui,self.ButtonField)
                ListObj=Target.split(".")
                ThisTarget=getattr(self.ui,ListObj[0])
            # for i in range(1,len(ListObj)):
            #     if ListObj[i] in self.__dict__.keys():
            #         ThisTarget=getattr(ThisTarget,ListObj[i])
                print self.ButtonField, ThisTarget
                QtCore.QObject.connect(Button, QtCore.SIGNAL(_fromUtf8(Type)), ThisTarget)
            else:
                print ModColor.Str("Not connect")
                
                

def dolink(ui,ButtonField="pushButton_FileName",Target="lineEdit_FileName",Type="lineEdit",args=None):

    # def selectFile():
    #     ui.lineEdit_FileName.setText(QtGui.QFileDialog.getOpenFileName())
    # ui.pushButton_FileName.clicked.connect(selectFile)
    Link=LinkClass(ui)
    Link.link(ButtonField,Target,Type)
    i=0
    while ("LinkClass%i"%i) in ui.__dict__.keys():
        i+=1
    setattr(ui,"LinkClass%i"%i,Link)

