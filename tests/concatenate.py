import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

a = [[1,2,3],[4,5,6]]
b = [[7,8,9],[10,11,12]]

g = np.concatenate([np.array(a), np.array(b)], axis=1)

s = nf.concatenate([nf.array(a), nf.array(b)], axis=1)

check_eq(__file__, g, s)
