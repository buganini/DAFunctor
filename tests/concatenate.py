import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

def f(np):
    a = [[1,2,3],[4,5,6]]
    b = [[7,8,9],[10,11,12]]

    return np.concatenate([np.array(a), np.array(b)], axis=1)

g = f(np)
s = f(nf)
check_eq("concatenate", g, s)
