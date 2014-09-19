# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License

from PyQt4.QtGui import QIcon
from PyQt4.QtDesigner import QPyDesignerCustomWidgetPlugin

import os
from matplotlib import rcParams
#from matplotlibButton_widget import MatplotlibWidget_button
#from widget_mpl_button import Ui_Form as MatplotlibWidget_button

from pyQtGraph_widget import pyQtGraphWidget


rcParams['font.size'] = 9


class pyQtGraphPlugin(QPyDesignerCustomWidgetPlugin):
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
        return pyQtGraphWidget(parent)

    def name(self):
        return "pyQtGraphWidget"

    def group(self):
        return "pyQtGraph"

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
        return '<widget class="pyQtGraphWidget" name="pyQtGraphWidget">\n' \
               '</widget>\n'

    def includeFile(self):
        return "pyQtGraph_widget"


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    widget = MatplotlibWidget()
    widget.show()
    sys.exit(app.exec_())
