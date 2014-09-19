import PyQt4
import sys
from PyQt4 import QtCore,QtGui

def start():
    return
    # app = QtCore.QCoreApplication.instance()
    # print "app",app
    # if app is None:
    #     app = PyQt4.QtGui.QApplication(sys.argv)
    # return app
    if not("app" in PyQt4.__dict__.keys()):
        pass
        #PyQt4.app=PyQt4.QtGui.QApplication(sys.argv)
        #QCoreApplication._exec()
        #QtCore.pyqtRemoveInputHook()
    return #PyQt4.app


def create_window(window_class):
    return
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration.
    """
    app_created = False
    #app = start()#QtCore.QCoreApplication.instance()
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        app_created = True
    app.references = set()
    window = window_class()
    app.references.add(window)
    window.app=app
    window.show()
    if app_created:
        #import threading
        app.exec_()
        #window.appThread=threading.Thread(target=app.exec_)
        #window.appThread.start()
    return window
