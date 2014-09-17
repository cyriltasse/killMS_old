
from distutils.core import setup
from Cython.Build import cythonize

# setup(
#   name = 'Hello world app',
#     ext_modules = cythonize(["MakeTOP_C.pyx","ClassModMatOp_C.pyx"]),
# )


setup(
    name = 'Hello world app',
    ext_modules = cythonize(["ClassSM.py","ClassSols.py","ClassTimeIt.py",
                             "logo.py","ModCluster.py","ModClusterRadial.py",
                             "ModColor.py","ModSMFromNp.py","MyLogger.py","MyPickle.py",
                             "progressbar.py","PseudoKill.py","rad2hmsdms.py","reformat.py",
                             "terminal.py","MakeTOP_C.py","ClassModMatOp_C.py"]),
)

