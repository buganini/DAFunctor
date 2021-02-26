from _tester import *

def f(np):
    a = [[1,2,3],[4,5,6]]
    b = [[7,8,9],[10,11,12]]

    return np.concatenate([np.array(a), np.array(b)], axis=1)

test_func("concatenate", f)
