import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
from dafunctor import jit

enable_jit = True

if enable_jit:
    from dafunctor import numpy
else:
    import numpy

@jit(enable_jit)
def func(a, b):
    m = numpy.meshgrid(a, b)
    meshgrid_a = m[0]
    meshgrid_b = m[1]
    return meshgrid_a, meshgrid_b

da = numpy.arange(5)
db = numpy.arange(7)

if enable_jit:
    a = func(da, db)
    print(a(da, db))
else:
    a = func(da, db)
    print(a)