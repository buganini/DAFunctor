import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import intro_tensor as it
import numpy
import pprint

pp = pprint.PrettyPrinter()

r = numpy.array(numpy.meshgrid([1,2],[3,4,5]))
print("numpy", r)

r = it.meshgrid([1,2],[3,4,5])
print("intro-tensor", r.eval())
r.output("float", "output")

print("===== CFG =====")
cfg = it.build_cfg([r])
pp.pprint(cfg)

print("===== C =====")
testbuild_dir = os.path.join(os.path.dirname(__file__), "..", "test-build")
os.makedirs(testbuild_dir, exist_ok=True)
c_name = os.path.basename(__file__)+".c"
c_path = os.path.join(testbuild_dir, c_name)
with open(c_path, "w") as f:
    it.gen_c(cfg, f)
print("Generated", c_path)

import tools
tools.test_c(c_path)