from tester_torch import *

def f(torch):
    a = [[[1],[2],[3]],[[4],[5],[6]]]
    return torch.Tensor(a)

test_func("tensor", f)
