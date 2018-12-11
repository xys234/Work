
from distutils.core import setup
from Cython.Build import cythonize
# cython: language_level=3

setup(name="fastloop", ext_modules=cythonize('fastloop.pyx'),)