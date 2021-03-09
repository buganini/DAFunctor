from tester_numpy import *

def add1(np):
    return np.add(np.array([[4,5],[6,7]]), 1)

test_func("add1", add1)

def add2(np):
    return np.array([[4,5],[6,7]]) + 2

test_func("add2", add2)

def add3(np):
    return np.array([[4,5],[6,7]]) + 2 + 3

test_func("add3", add3)
