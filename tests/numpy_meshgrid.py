from tester_numpy import *

def f1(np):
    r = np.array(np.meshgrid([1,2],[3,4,5]))
    return r

test_func("meshgrid_data", f1)

def f2(np):
    return np.array(np.meshgrid(np.arange(1,3),np.arange(3,6),[7,8,9,10]))

test_func("meshgrid_arange", f2)
