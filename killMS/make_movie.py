#!/usr/bin/env python

import os
import sys

def make_movie(prefix,outn):
    #strr="mencoder -ovc lavc -lavcopts vcodec=mpeg4:vpass=1:vbitrate=6160000:mbd=2:keyint=132:v4mv:vqmin=3:lumi_mask=0.07:dark_mask=0.2:mpeg_quant:scplx_mask=0.1:tcplx_mask=0.1:naq -mf type=png:fps=10 -nosound -o %s mf://\%s*.png"%(outn,prefix)
    strr="mencoder -ovc lavc -lavcopts vcodec=mpeg4:vpass=1:vbitrate=6160000:mbd=2:keyint=132:v4mv:vqmin=3:lumi_mask=0.07:dark_mask=0.2:mpeg_quant:scplx_mask=0.1:tcplx_mask=0.1:naq -mf type=png:fps=10 -nosound -o %s mf://\%s*.png"%(outn,prefix)

    #strr='/home/tasse/bin/ffmpeg -i "Fig%5d.png" -c:v libx264 -preset slow -crf 22 -c:a copy output.mkv'%(outn,prefix)

    #strr='/home/tasse/bin/ffmpeg -i "Fig%5d.png" -c:v libx264 -preset ultrafast -qp 0 output.mkv'
    
    print strr
    os.system(strr)

if __name__=="__main__":
    prefix=sys.argv[1]
    outn=sys.argv[2]
    make_movie(prefix,outn)

