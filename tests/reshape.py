import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import numpy as np
import ndafunctor as nf

a = [[1,2,3],[4,5,6]]

g = np.reshape(np.array(a), (1,2,1,3,1))

s = nf.reshape(nf.array(a), (1,2,1,3,1))

check_eq(__file__, g, s)
