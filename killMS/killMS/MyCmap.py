
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors

def DefMyRedBlue():
    ccut=0.
    gmax=0.
    rmax=0.7
    bmax=0.7
    
    r1,g1,b1=matplotlib.colors.hex2color("#245BFF") # blue

    rmid,gmid,bmid=matplotlib.colors.hex2color("#FFFFFF")

    r2,g2,b2=matplotlib.colors.hex2color("#FF242D") #red



    cdict1 = {'red':   ((0.0, r1,r1),
                        (0.5, rmid,rmid),
                        (1.0, r2,r2)),
              
              'green': ((0.0, g1,g1),
                        (0.5, gmid,gmid),
                        (1.0, g2, g2)),
              
              'blue':  ((0.0, b1,b1),
                        (0.5, bmid,bmid),
                        (1.0, b2,b2))
              }


    # al0=0.1
    # cdict1['alpha'] = ((0.0, 1.0, 1.0),
    #                    (0.5, al0, al0),
    #                    (1.0, 1.0, 1.0))
    
    plt.register_cmap(name='MyRedBlue', data=cdict1)

DefMyRedBlue()
