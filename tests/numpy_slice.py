from tester_numpy import *

def f_int(np, d):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[d]

test_func("slice_int_0", f_int, 0)
test_func("slice_int_1", f_int, 1)
test_func("slice_int__1", f_int, -1)

def f_range(np):
    a = [[[1],[2],[3]],[[4],[5],[6]],[[7],[8],[9]]]
    return np.array(a)[1:3]

test_func("slice_range", f_range)

def f_range_step(np):
    a = [0,1,2,3,4,5,6,7,8,9]
    return np.array(a)[2:-2:2]

test_func("slice_range_step", f_range_step)

def f_range_step2(np):
    a = list(range(50))
    return np.array(a)[2:-2:2][3:15:7]

test_func("slice_range_step2", f_range_step2)

def f_tuple(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[1:,:]

test_func("slice_tuple_1", f_tuple)

def f_tuple2(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[:,1:]

test_func("slice_tuple_2", f_tuple2)

def f_tuple_mixed(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)[1:,1]

test_func("slice_tuple_mixed", f_tuple_mixed)

def f_tuple_mixed_step(np):
    a = [[[1],[2],[3],[4],[5],[6]],[[7],[8],[9],[10],[11],[12]]]
    return np.array(a)[1:,1::2]

test_func("slice_tuple_mixed_step", f_tuple_mixed_step)
