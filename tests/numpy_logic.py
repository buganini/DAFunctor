from tester_numpy import *

def f_greater(np):
    a = np.array([1,2,3])
    b = np.array([3,2,1])
    return np.greater(a, b)

test_func("greater", f_greater)
