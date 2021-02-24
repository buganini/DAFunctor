import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import ndafunctor as nf
import numpy
import pprint

pp = pprint.PrettyPrinter()

r = numpy.zeros((2,3,4))
print("numpy", r)

r = nf.zeros((2,3,4))
print("ndafunctor", r.eval())
r.output("float", "output")

print("===== CFG =====")
cfg = nf.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
f = r.jit()
print("ndafunctor-C", f())
