from tester_torch import *

def f_permute(torch):
    return torch.Tensor([[4,5],[6,7]]).permute((1,0))

test_func("permute", f_permute)

