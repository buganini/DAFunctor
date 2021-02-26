import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

def f(np):
    return np.arange(1,5,2)

g = f(np)
s = f(nf)
check_eq("arange", g, s)
