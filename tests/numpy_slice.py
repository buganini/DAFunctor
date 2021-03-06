from tester_numpy import *

def f0(np, d):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[d]

test_func("slice_int_0", f0, 0)
test_func("slice_int_1", f0, 1)

def f1(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[2:3]

test_func("slice_range", f1)

def f2(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[1:,:]

test_func("slice_tuple_1", f2)

def f3(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[:,1:]

test_func("slice_tuple_2", f3)
