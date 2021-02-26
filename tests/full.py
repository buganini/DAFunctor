import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import numpy as np
import ndafunctor as nf

def f(np):
    return np.full((2,3,4),7)

g = f(np)
s = f(nf)
check_eq(__file__, g, s)
