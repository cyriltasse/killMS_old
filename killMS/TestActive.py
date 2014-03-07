
from progressbar import ProgressBar

def Print():
    pbar=ProgressBar()
    pbar.render(50)
    ProgressBar.silent=1
    pbar.render(90)

    
