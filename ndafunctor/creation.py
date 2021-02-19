from .functor import Functor
from .manipulation import *

def arange(*args):
    if len(args) == 1:
        start = 0
        end = args[0]
        step = 1
    elif len(args) == 2:
        start = args[0]
        end = args[1]
        step = 1
    elif len(args) == 3:
        start = args[0]
        end = args[1]
        step = args[2]
    else:
        raise NotImplementedError("arange")

    data = [start,end,step]
    shape = [(end - start) // step]
    return Functor(
        shape,
        dexpr = ["+","d0","*","i0","d2"], # start + i * step
        iexpr = [["i0"]],
        data = data,
        desc = "arange"
    )

def raw_meshgrid(*args):
    regs = args
    n = [len(args)]
    for i in range(len(args)):
        n.append(len(args[i]))
    f = ["ref","ref","r","i0","ref","i","+","i0","1"] # r[i0][i[i0+1]]
    return Functor(regs, n, f)

def meshgrid(*args):
    if len(args)>1:
        d = list(range(len(args)+1))
        d = [d[0],d[2],d[1]] + d[3:]
        return transpose(raw_meshgrid(*args), d)
    else:
        return raw_meshgrid(*args)
