import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy as np

g = np.array(np.meshgrid([1,2],[3,4,5],[6,7,8,9]))

s = nf.meshgrid([1,2],[3,4,5],[6,7,8,9])

check_eq(__file__, g, s)
