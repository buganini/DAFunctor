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
def func():
    var_a = numpy.arange(5,10)
    return var_a

if enable_jit:
    a = func()
    print(a())
else:
    a = func()
    print(a)