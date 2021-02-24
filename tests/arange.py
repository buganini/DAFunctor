import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

g = np.arange(1,5,2)

s = nf.arange(1,5,2)

check_eq(__file__, g, s)
