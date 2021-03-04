from _tester import *

a = [[[1],[2],[3]],[[4],[5],[6]]]

def f0(np, d):
    return np.array(a)[d]

test_func("slice_int_0", f0, 0)
test_func("slice_int_1", f0, 1)

def f1(np):
    return np.array(a)[2:3]

test_func("slice_slice", f1)

def f2(np):
    return np.array(a)[1:,:]

test_func("slice_tuple_1", f2)

def f3(np):
    return np.array(a)[:,1:]

test_func("slice_tuple_2", f3)
