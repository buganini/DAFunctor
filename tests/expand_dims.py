from _tester import *

def f(np):
    return np.expand_dims(np.arange(1,6), axis=1)

test_func("expand_dims", f)
