from _tester import *

def f(np):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return np.array(a)

test_func("array", f)
