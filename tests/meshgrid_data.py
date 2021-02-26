from _tester import *

def f(np):
    r = np.meshgrid([1,2],[3,4,5],[6,7,8,9])
    if type(r) is list:
        r = np.array(r)
    return r

test_func("meshgrid_data", f)
