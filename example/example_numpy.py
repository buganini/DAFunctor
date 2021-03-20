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
def demo_func(data_a, data_b):
    meshgrid_a, meshgrid_b = numpy.meshgrid(data_a, data_b)
    return meshgrid_a, meshgrid_b

da = numpy.arange(5)
db = numpy.arange(7)

r = demo_func(da, db)

print(r)

if enable_jit:
    print(open(demo_func(get_source=True)).read())
