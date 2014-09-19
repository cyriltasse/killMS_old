import os.path as osp

#from guiqwt.plot import CurveDialog as ImageDialog
#from guiqwt.plot import ImageWidgetMixin as ImageDialog
from MyPlot import ImageDialog

from guiqwt.builder import make
import StartApp
def test():
    """Test"""
    # -- Create QApplication
    import guidata
    _app = StartApp.start()#guidata.qapplication()
    # --    
    filename = osp.join(osp.dirname(__file__), "brain.png")
    image = make.image(filename=filename, title="Original", colormap='gray')
    
    #win = ImageDialog(edit=False, toolbar=True, wintitle="Contrast test", options=dict(show_contrast=True))
    win = ImageDialog( toolbar=True, wintitle="Contrast test", options=dict(show_contrast=True))
    plot = win.get_plot()
    plot.add_item(image)
    win.resize(600, 600)
    win.show()
    # try:
    #     plot.save_widget('contrast.png')
    # except IOError:
    #     # Skipping this part of the test 
    #     # because user has no write permission on current directory
    #     pass
    #win.exec_()
    return win


if __name__ == "__main__":
    test()
