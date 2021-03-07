from tester_numpy import *

def f1(np):
    return np.arange(1,5,2)

test_func("arange", f1)

def f2(np):
    return np.arange(1,5000,7)

test_func("arange_long", f2)
