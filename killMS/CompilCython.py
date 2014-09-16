from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Hello world app',
    ext_modules = cythonize(["MakeTOP_C.pyx","ClassModMatOp_C.pyx"]),
)
