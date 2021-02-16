import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import intro_tensor as it
import numpy

# r = np.arange(3)
# print(r.eval())


r = numpy.array(numpy.meshgrid([1,2],[3,4])).transpose(0,2,1)
print("numpy", r)

r = it.raw_meshgrid([1,2],[3,4])
print("intro-tensor", r.eval())

r = numpy.array(numpy.meshgrid([1,2],[3,4]))
print("numpy", r)

r = it.meshgrid([1,2],[3,4])
print("intro-tensor", r.eval())