from tester_numpy import *

def f1(np):
    a = [[1,2,3],[4,5,6]]
    return np.reshape(np.array(a), (1,2,1,3,1))

test_func("reshape1", f1)

def f2(np):
    a = [[1,2,3],[4,5,6]]
    return np.reshape(np.reshape(np.array(a), (1,2,1,3,1)), (3,2))

test_func("reshape2", f2)

def f3(np):
    a = [[1,2,3,4]]
    return np.reshape(np.array(a), (2,2))

test_func("reshape3", f3)
