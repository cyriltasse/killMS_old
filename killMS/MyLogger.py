import logging
import sys
 
class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

import ModColor

class MyLogger():
    def __init__(self):
#fmt="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        fmt=" - %(asctime)s - %(name)-25.25s |   %(message)s"
        datefmt='%H:%M:%S'#'%H:%M:%S.%f'
        logging.basicConfig(level=logging.DEBUG,format=fmt,datefmt=datefmt)
        self.Dico={}


    def getLogger(self,name):
        if not(name in self.Dico.keys()):
            logger = logging.getLogger(name)
            fp = LoggerWriter(logger, logging.INFO)
            self.Dico[name]=fp
        
        self.Dico[name].logger.log(logging.DEBUG, "Get Logger for: %s"%name)
        return self.Dico[name]



    #logger2 = logging.getLogger("demo.X")
    #debug_fp = LoggerWriter(logger2, logging.DEBUG)
    #print>>fp, ModColor.Str("An INFO message")
    #print >> debug_fp, "A DEBUG message"
    #print >> debug_fp, 1

M=MyLogger()

getLogger=M.getLogger

if __name__=="__main__":
    log=getLogger("a.x")
    print>>log, "a.x"
