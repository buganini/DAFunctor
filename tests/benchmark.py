from tester_numpy import *
from dafunctor import Buffer
import numpy

def bench1(n):
    A = numpy.random.rand(n,n).astype(numpy.single)
    B = numpy.random.rand(n,n).astype(numpy.single)

    A = A.tobytes()
    B = B.tobytes()

    A  = Buffer("data1", "f", A)
    B  = Buffer("data2", "f", B)

    def f(np, A, B):
        if np is numpy:
            A = A.buffer
            B = B.buffer

        A = np.reshape(np.frombuffer(A, dtype=np.single), (n,n))
        B = np.reshape(np.frombuffer(B, dtype=np.single), (n,n))

        # return A*B-1*A
        return A*B-4.1*A > 2.5*B

    test_func(f"bench1_{n}", f, A, B, params=[A, B])

# https://nbviewer.jupyter.org/github/rasbt/One-Python-benchmark-per-day/blob/master/ipython_nbs/day7_2_jit_numpy.ipynb
for i in range(1,5):
    bench1(10**i)
