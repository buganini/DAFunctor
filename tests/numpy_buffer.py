import struct
from tester_numpy import *
import numpy
from dafunctor import Buffer

data1 = struct.pack("ffff", 0.1, 0.2, 0.3, 0.4)
buf1  = Buffer("data1", "f", data1)

data2 = struct.pack("ffff", 0.5, 0.6, 0.7, 0.8)
buf2  = Buffer("data2", "f", data2)

def func1(np, b):
    if np is numpy:
        b = b.buffer
    a = np.frombuffer(b, dtype=np.single)
    return np.reshape(a, (2,2))

test_func("buffer1", func1, buf1, params=[buf1])

def func2(np, b1, b2):
    if np is numpy:
        b1 = b1.buffer
        b2 = b2.buffer
    a1 = np.frombuffer(b1, dtype=np.single)
    a2 = np.frombuffer(b2, dtype=np.single)
    return np.reshape(np.add(a1, a2), (2,2))

test_func("buffer2", func2, buf1, buf2, params=[buf1, buf2])


def func3(np, b1, b2):
    if np is numpy:
        b1 = b1.buffer
        b2 = b2.buffer
    a1 = np.frombuffer(b1, dtype=np.single)
    a2 = np.frombuffer(b2, dtype=np.single)
    return np.reshape(np.add(np.add(a1, 2), a2), (2,2))

test_func("buffer3", func3, buf1, buf2, params=[buf1, buf2])
