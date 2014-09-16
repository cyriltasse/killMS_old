import numpy as np

def append_field(rec, name, arr, dtype=None):
    arr = np.asarray(arr)
    if dtype is None:
        dtype = arr.dtype
    newdtype = np.dtype(rec.dtype.descr + [(name, dtype)])
    newrec = np.empty(rec.shape, dtype=newdtype)
    for field in rec.dtype.fields:
        newrec[field] = rec[field]
    
    newrec[name] = arr
    return newrec

def append_field2(rec, name, arr, dtype=None):
    arr = np.asarray(arr)
    if dtype is None:
        dtype = arr.dtype
    newdtype = np.dtype(rec.dtype.descr + [(name, dtype, (arr.shape[1:]))])
    newrec = np.empty(rec.shape, dtype=newdtype)
    for field in rec.dtype.fields:
        newrec[field] = rec[field]
    
    newrec[name] = arr
    return newrec

def append_field3(rec, name, rec2):
    d0=rec.dtype.descr
    d1=rec2.dtype.descr
    rec2=np.asarray(rec2)
    if rec.shape[0]==rec2.shape[0]:
        d2=d0+[(name,d1,rec2.shape[1:])]
        a=np.zeros(rec.shape[0],dtype=d2)
    else:
        d2=d0+[(name,d1,(rec.shape[0],rec2.shape))]
        a=np.zeros(rec.shape[0],dtype=d2)

    for field in rec.dtype.fields:
        a[field] = rec[field]
    a[name]=rec2
    return a.view(np.recarray)
