import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import ndafunctor as nf
import pprint

pp = pprint.PrettyPrinter()

a = [[1,2,3],[4,5,6]]
r = np.reshape(np.array(a), (1,2,1,3,1))
print("numpy", r)

r = nf.reshape(nf.array(a), (1,2,1,3,1))
print("ndafunctor", r.eval())
r.output("float", "output")

cfg = nf.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
testbuild_dir = os.path.join(os.path.dirname(__file__), "..", "test-build")
os.makedirs(testbuild_dir, exist_ok=True)
c_name = os.path.basename(__file__)+".c"
c_path = os.path.join(testbuild_dir, c_name)
with open(c_path, "w") as f:
    nf.gen_c(cfg, f)
print("Generated", c_path)

import tools
tools.test_c(c_path)