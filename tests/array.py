import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import ndafunctor as nf
import pprint

pp = pprint.PrettyPrinter()

a = [[[1],[2],[3]],[[4],[5],[6]]]
r = np.array(a)
print("numpy", r)

r = nf.array(a)
print("ndafunctor", r.eval())
r.output("float", "output")

cfg = nf.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
f = r.jit()
print("ndafunctor-C", f())
