import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

def f(np):
    r = np.meshgrid([1,2],[3,4,5],[6,7,8,9])
    if type(r) is list:
        r = np.array(r)
    return r

g = f(np)
s = f(nf)
check_eq("meshgrid_data", g, s)
