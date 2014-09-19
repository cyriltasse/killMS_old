# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License

from PyQt4.QtGui import QIcon
from PyQt4.QtDesigner import QPyDesignerCustomWidgetPlugin

import os
from matplotlib import rcParams
from matplotlibButton_widget import MatplotlibWidget_button
#from widget_mpl_button import Ui_Form as MatplotlibWidget_button



rcParams['font.size'] = 9


class MatplotlibPlugin_button(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QPyDesignerCustomWidgetPlugin.__init__(self)

        self._initialized = False

    def initialize(self, formEditor):
        if self._initialized:
            return

        self._initialized = True

    def isInitialized(self):
        return self._initialized

    def createWidget(self, parent):
        return MatplotlibWidget_button(parent)

    def name(self):
        return "MatplotlibWidget_button"

    def group(self):
        return "Python(x,y)"

    def icon(self):
        image = os.path.join(rcParams['datapath'], 'images', 'matplotlib.png')
        return QIcon(image)

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="MatplotlibWidget_button" name="mplwidget_button">\n' \
               '</widget>\n'

    def includeFile(self):
        return "matplotlibButton_widget"


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    widget = MatplotlibWidget()
    widget.show()
    sys.exit(app.exec_())
