import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

def f1(np):
    return np.repeat(2, 3)

g = f1(np)
s = f1(nf)
check_eq(__file__, g, s)

def f2(np, axis):
    return np.repeat(np.array([[1,2,3],[4,5,6]]), 3, axis=axis)

g = f2(np, 0)
s = f2(nf, 0)
check_eq(__file__, g, s)

g = f2(np, 1)
s = f2(nf, 1)
check_eq(__file__, g, s)

# g = f2(np, None)
# s = f2(nf, None)
# check_eq(__file__, g, s)

def f3(np):
    return np.repeat(np.repeat(np.array([1,2]), 2, axis=0), 2, axis=0)

g = f3(np)
s = f3(nf)
check_eq(__file__, g, s)
