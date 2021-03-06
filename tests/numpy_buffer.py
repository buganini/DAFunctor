import struct
from tester_numpy import *
import numpy
from ndafunctor import Buffer

def f(np, b):
    if np is numpy:
        b = b.buffer
    a = np.frombuffer(b, dtype=np.single)
    return np.reshape(a, (2,2))

data = struct.pack("ffff", 0.1, 0.2, 0.3, 0.4)
buf  = Buffer("data", "f", data)

test_func("buffer", f, buf, params=[buf])
