from _tester import *

def f(np):
    return np.stack([np.arange(1,6), np.arange(5,10)], axis=1)

test_func("stack", f)
