import os

def install():
    os.system("python CompilCython.py build_ext --inplace")
    os.system("mkdir bin")
    os.system("cp *.so bin/.")
    os.system("cp CHMOD.sh ClassMS.py ClassPredict.py  killMS.py  MakeModel.py dsreg.py bin/.")

if __name__=="__main__":
    install()
