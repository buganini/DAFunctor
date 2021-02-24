import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

g = np.expand_dims(np.arange(1,6), axis=1)

s = nf.expand_dims(nf.arange(1,6), axis=1)

check_eq(__file__, g, s)
