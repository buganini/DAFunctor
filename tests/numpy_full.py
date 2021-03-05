from tester_numpy import *

def f(np):
    return np.full((2,3,4),7)

test_func("full", f)
