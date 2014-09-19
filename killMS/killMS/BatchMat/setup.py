from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os

import numpy as np

include_dirs = ['/usr/include', np.get_include(), '/usr/include/atlas', '/usr/include/python2.7/pysparse']
library_dirs = ['/usr/lib']
libraries = ['lapack', 'lapack_atlas', 'blas', 'atlas'] ## ['blas', 'atlas']

ext_modules = []
for extension in ('smt',):
    ext_modules += [Extension(extension, [extension + '.pyx'],
                              libraries=libraries,
                              library_dirs=library_dirs,
                              include_dirs=include_dirs)]
setup(
  name = 'BLAS and LAPACK wrapper',
##  name = 'BLAS wrapper',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules,
)
