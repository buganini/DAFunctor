from _tester import *

def f1(np):
    r = np.meshgrid([1,2],[3,4,5])
    if type(r) is list:
        r = np.array(r)
    return r

test_func("meshgrid_data", f1)

def f2(np):
    return np.array(np.meshgrid(np.arange(1,3),np.arange(3,6),np.arange(7,11)))

test_func("meshgrid_arange", f2)
