from _tester import *

def f(np, axis):
    return np.stack([np.array([[1,2,3],[4,5,6]]), np.array([[7,8,9],[10,11,12]])], axis=axis)

test_func("stack", f, 0)
test_func("stack", f, 1)
