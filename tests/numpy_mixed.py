from tester_numpy import *

def f1(np):
    return np.stack([np.array([[1,2,3],[4,5,6]]), np.array([[7,8,9],[10,11,12]])], axis=0) + 1

test_func("mixed1", f1)
