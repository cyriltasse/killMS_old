# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_mpl_button.ui'
#
# Created: Thu Oct 31 15:01:31 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(630, 509)
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setGeometry(QtCore.QRect(10, 10, 608, 493))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mplwidget = MatplotlibWidget(self.verticalLayoutWidget)
        self.mplwidget.setObjectName(_fromUtf8("mplwidget"))
        self.verticalLayout_2.addWidget(self.mplwidget)
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.doubleSpinBox_vmax = QtGui.QDoubleSpinBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_vmax.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_vmax.setSizePolicy(sizePolicy)
        self.doubleSpinBox_vmax.setMinimumSize(QtCore.QSize(55, 0))
        self.doubleSpinBox_vmax.setMaximumSize(QtCore.QSize(95, 16777215))
        self.doubleSpinBox_vmax.setReadOnly(False)
        self.doubleSpinBox_vmax.setMinimum(-100000.0)
        self.doubleSpinBox_vmax.setMaximum(100000.0)
        self.doubleSpinBox_vmax.setObjectName(_fromUtf8("doubleSpinBox_vmax"))
        self.verticalLayout.addWidget(self.doubleSpinBox_vmax)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalSlider_vmax = QtGui.QSlider(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalSlider_vmax.sizePolicy().hasHeightForWidth())
        self.verticalSlider_vmax.setSizePolicy(sizePolicy)
        self.verticalSlider_vmax.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.verticalSlider_vmax.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_vmax.setObjectName(_fromUtf8("verticalSlider_vmax"))
        self.horizontalLayout.addWidget(self.verticalSlider_vmax)
        self.label_vmax = QtGui.QLabel(self.widget)
        self.label_vmax.setObjectName(_fromUtf8("label_vmax"))
        self.horizontalLayout.addWidget(self.label_vmax)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.doubleSpinBox_mean = QtGui.QDoubleSpinBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_mean.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_mean.setSizePolicy(sizePolicy)
        self.doubleSpinBox_mean.setMinimumSize(QtCore.QSize(55, 0))
        self.doubleSpinBox_mean.setMinimum(-100000.0)
        self.doubleSpinBox_mean.setMaximum(100000.0)
        self.doubleSpinBox_mean.setObjectName(_fromUtf8("doubleSpinBox_mean"))
        self.verticalLayout.addWidget(self.doubleSpinBox_mean)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalSlider_vmin = QtGui.QSlider(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalSlider_vmin.sizePolicy().hasHeightForWidth())
        self.verticalSlider_vmin.setSizePolicy(sizePolicy)
        self.verticalSlider_vmin.setMinimumSize(QtCore.QSize(20, 0))
        self.verticalSlider_vmin.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_vmin.setInvertedAppearance(True)
        self.verticalSlider_vmin.setInvertedControls(False)
        self.verticalSlider_vmin.setObjectName(_fromUtf8("verticalSlider_vmin"))
        self.horizontalLayout_2.addWidget(self.verticalSlider_vmin)
        self.label_vmin = QtGui.QLabel(self.widget)
        self.label_vmin.setObjectName(_fromUtf8("label_vmin"))
        self.horizontalLayout_2.addWidget(self.label_vmin)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.doubleSpinBox_vmin = QtGui.QDoubleSpinBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_vmin.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_vmin.setSizePolicy(sizePolicy)
        self.doubleSpinBox_vmin.setMinimumSize(QtCore.QSize(55, 0))
        self.doubleSpinBox_vmin.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox_vmin.setMinimum(-100000.0)
        self.doubleSpinBox_vmin.setMaximum(100000.0)
        self.doubleSpinBox_vmin.setObjectName(_fromUtf8("doubleSpinBox_vmin"))
        self.verticalLayout.addWidget(self.doubleSpinBox_vmin)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_vmax.setText(_translate("Form", "TextLabel", None))
        self.label_vmin.setText(_translate("Form", "TextLabel", None))

from matplotlibwidget import MatplotlibWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

