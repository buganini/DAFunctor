from tester_numpy import *

def f_greater(np):
    a = np.array([1,2,4,8])
    b = np.array([0,1,1,6])
    return np.greater(a, b)

test_func("greater", f_greater)
