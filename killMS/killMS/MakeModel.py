#!/usr/bin/env python

import optparse
import ClassSM


def read_options():
    desc="""Questions and suggestions: cyril.tasse@obspm.fr"""
    global options
    opt = optparse.OptionParser(usage='Usage: %prog <options>',version='%prog version 1.0',description=desc)
    group = optparse.OptionGroup(opt, "* Data-related options", "Won't work if not specified.")
    group.add_option('--SkyModel',help='List of targets [no default]',default='')
    group.add_option('--NCluster',help=' Default is %default',default="0")
    group.add_option('--DoPlot',help=' Default is %default',default="1")
    group.add_option('--DoSelect',help=' Default is %default',default="0")
    group.add_option('--DoPrint',help=' Default is %default',default="0")
    group.add_option('--CMethod',help=' Clustering method [1,2,3]. Default is %default',default="1")
    opt.add_option_group(group)
    options, arguments = opt.parse_args()
    
if __name__=="__main__":
    read_options()
    NCluster=int(options.NCluster)
    DoPlot=(int(options.DoPlot)==1)
    DoSelect=(int(options.DoSelect)==1)
    CMethod=int(options.CMethod)
    SM=ClassSM.ClassSM(options.SkyModel,ReName=True,
                       DoREG=True,SaveNp=True,
                       NCluster=NCluster,DoPlot=DoPlot,
                       SelSource=DoSelect,ClusterMethod=CMethod)
    if options.DoPrint=="1":
        SM.print_sm2()
