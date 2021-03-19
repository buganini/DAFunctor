import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
from dafunctor import jit, numpy

@jit(True)
def func():
    var_a = numpy.arange(5,10)
    return var_a

a = func()

print(a)