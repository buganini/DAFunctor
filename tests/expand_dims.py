import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import ndafunctor as nf
import numpy as np
import pprint

pp = pprint.PrettyPrinter()

r = np.expand_dims(np.arange(1,6), axis=1)
print("numpy", r)

r = nf.expand_dims(nf.arange(1,6), axis=1)

print("ndafunctor", r.eval())
r.output("float", "output")

print("===== CFG =====")
cfg = nf.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
f = r.jit()
print("ndafunctor-C", f())
