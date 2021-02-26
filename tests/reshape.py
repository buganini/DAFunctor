from _tester import *

def f(np):
    a = [[1,2,3],[4,5,6]]
    return np.reshape(np.array(a), (1,2,1,3,1))

test_func("reshape", f)
