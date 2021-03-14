from tester_numpy import *

def f_transpose(np):
    return np.transpose(np.array([[4,5],[6,7]]), (1,0))

test_func("transpose", f_transpose)

