from _tester import *

def f(np, axis):
    a = [[1,2,3],[4,5,6]]
    b = [[7,8,9],[10,11,12]]

    return np.concatenate([np.array(a), np.array(b)], axis=axis)

test_func("concatenate", f, 0)
test_func("concatenate", f, 1)
