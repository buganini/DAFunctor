import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

def f(np):
    return np.expand_dims(np.arange(1,6), axis=1)

g = f(np)
s = f(nf)
check_eq("expand_dims", g, s)
