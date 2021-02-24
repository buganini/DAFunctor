import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tools import *
import ndafunctor as nf
import numpy

g = numpy.zeros((2,3,4))

s = nf.zeros((2,3,4))

check_eq(__file__, g, s)
