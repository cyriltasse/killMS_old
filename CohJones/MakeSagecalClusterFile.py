#!/usr/bin/env python

import optparse
import sys
import MyPickle


import ModColor

import time
import os
import numpy as np
import pickle
import ClassMS
import ClassSM
from ClassPredict import ClassPredict
import PseudoKill
import ClassTimeIt

Name="ConvertModel"

def read_options():
    opt = optparse.OptionParser(usage='Usage: %prog --ms=somename.MS <options>',version='%prog version 1.0')
    group = optparse.OptionGroup(opt, "* Data-related options", "Won't work if not specified.")
    group.add_option('--CohSkyModel',help='Input Cohjones SM [no default]',default='')
    group.add_option('--SageSkyModel',help='Input Sagecal SM [no default]',default='')
    opt.add_option_group(group)
    
    
    options, arguments = opt.parse_args()
    
    f = open("last_%s.obj"%Name,"wb")
    pickle.dump(options,f)

import ClassSM
def main(options=None):
    if options==None:
        f = open("last_%s.obj"%Name,'rb')
        options = pickle.load(f)

    SM=ClassSM.ClassSM(options.CohSkyModel)

    SageSources=[]
    ifile  = open(options.SageSkyModel, "rb")
    while True:
        line=ifile.readline()
        if line=="": break
        if line[0]=="#": continue
        name=line.split(" ")[0]
        SageSources.append(name)
    ifile.close()
    Clusters=SM.SourceCat.Cluster
    Cat=np.zeros((len(SageSources),),dtype=[('Name','|S200'),('Cluster',np.int)])
    Cat=Cat.view(np.recarray)
    Cat.Name[:]=np.array(SageSources)
    Cat.Cluster[:]=np.array(Clusters)
    
    OutFile="%s.cluster"%options.SageSkyModel
    f = open(OutFile,'w')
    for iCluster in range(np.max(Cat.Cluster)+1):

        ind=np.where(Cat.Cluster==iCluster)[0]
        CNames=Cat.Name[ind].tolist()
        LCNames=" ".join(CNames)

        f.write("%i %i %s\n"%(iCluster, 1, LCNames))
    f.close()

if __name__=="__main__":
    read_options()
    f = open("last_%s.obj"%Name,'rb')
    options = pickle.load(f)
    main(options=options)

