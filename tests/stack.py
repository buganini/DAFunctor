import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np


g = np.stack([np.arange(1,6), np.arange(5,10)], axis=1)

s = nf.stack([nf.arange(1,6), nf.arange(5,10)], axis=1)

check_eq(__file__, g, s)
