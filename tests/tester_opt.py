import struct
from tester_numpy import *
import numpy
from dafunctor import Buffer

data1 = struct.pack("ffff", 0.1, 0.2, 0.3, 0.4)
buf1  = Buffer("f", data1, "buf1")

def tail_reshape(np, b):
    if np is numpy:
        b = b.buffer
    a = np.frombuffer(b, dtype=np.single)
    return np.reshape(np.reshape(a, (4,1)), (2,2))

test_func("opt_reshape", tail_reshape, buf1, params=[buf1], visualize=True)

#######

n = 1000

A = numpy.random.rand(n,n).astype(numpy.single)
B = numpy.random.rand(n,n).astype(numpy.single)

A = A.tobytes()
B = B.tobytes()

A  = Buffer("f", A, "data_a")
B  = Buffer("f", B, "data_b")

def benchmark(np, A, B):
    if np is numpy:
        A = A.buffer
        B = B.buffer

    A = np.reshape(np.frombuffer(A, dtype=np.single), (n,n))
    B = np.reshape(np.frombuffer(B, dtype=np.single), (n,n))

    # return A*B-1*A
    return A*B-4.1*A > 2.5*B

test_func("opt_reshape2", benchmark, A, B, params=[A, B], eval_test=False, visualize=True)
