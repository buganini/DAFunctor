import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import ndafunctor as nf
import numpy as np
import pprint

pp = pprint.PrettyPrinter()

r = np.array(np.meshgrid([1,2],[3,4,5]))
print("numpy", r)

r = nf.meshgrid([1,2],[3,4,5])
print("ndafunctor", r.eval())
r.output("float", "output")

print("===== CFG =====")
cfg = nf.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
f = r.jit()
print("ndafunctor-C", f())
