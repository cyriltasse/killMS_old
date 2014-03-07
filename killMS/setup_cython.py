from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("BatchMatInverse_C", ["BatchMatInverse_C.pyx"])]
)

# setup(
#     cmdclass = {'build_ext': build_ext},
#     ext_modules = [Extension("IonImager10_C2", ["IonImager10_C2.pyx"])]
# )

# setup(
#     cmdclass = {'build_ext': build_ext},
#     ext_modules = [Extension("Cluster_C", ["Cluster_C.pyx"])]
# )
