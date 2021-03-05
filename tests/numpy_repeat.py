from tester_numpy import *

def f1(np):
    return np.repeat(2, 3)

test_func("repeat_value", f1)

def f2(np, axis=None):
    return np.repeat(np.array([[1,2,3],[4,5,6]]), 3, axis=axis)

test_func("repeat_axis_0", f2, 0)

test_func("repeat_axis_1", f2, 1)

test_func("repeat_axis_none", f2)

def f3(np):
    return np.repeat(np.repeat(np.array([1,2]), 2, axis=0), 2, axis=0)

test_func("repeat_nested", f3)
