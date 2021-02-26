import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import numpy as np
import ndafunctor as nf

def f(np):
    a = [[1,2,3],[4,5,6]]
    return np.reshape(np.array(a), (1,2,1,3,1))

g = f(np)
s = f(nf)
check_eq("reshape", g, s)
