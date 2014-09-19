import sys
import numpy as np

def Go(Obj):
    
    for property, value in vars(Obj).iteritems():
        if type(value)==np.ndarray:
            size=value.nbytes
        else:
            size=sys.getsizeof(value)
            
        print "%30s: %10s Bytes"%(property, str(size))
