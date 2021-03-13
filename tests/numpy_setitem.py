from tester_numpy import *

def f_int_value(np):
    a = np.arange(10)
    a[5] = 100
    return a

test_func("setitem_int_value", f_int_value)

def f_int_functor(np):
    a = np.reshape(np.arange(27),(3,3,3))
    a[2] = np.reshape(np.arange(500,500+9),(3,3))
    return a

test_func("setitem_int_functor", f_int_functor)

def f_range(np):
    a = np.arange(10)
    a[2:7] = 100
    return a

test_func("setitem_range", f_range)


def f_range_step(np):
    a = np.arange(10)
    a[2:7:2] = 100
    return a

test_func("setitem_range_step", f_range_step)
