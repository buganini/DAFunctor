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
        data = data,
        desc = "arange"
    )

def raw_meshgrid(*args):
    shape = [range(1,len(args)+1)]
    for i in range(len(args)):
        shape.append(len(args[i]))
    # data[i0][i[i0+1]]
    subs = []
    for i in range(len(args)):
        subs.append(Functor(
            shape[1:],
            dexpr = ["ref","d","i{}".format(i)], # data[i{i0+1}]]
            data = args[i],
            desc = "raw_meshgrid[{}]".format(i)
        ))
    iexpr = [["0"]]
    for i in range(len(shape)-1):
        iexpr.append(["i{}".format(i)])
    return Functor(
        shape,
        iexpr = iexpr,
        subs = subs,
        desc = "raw_meshgrid"
    )

def meshgrid(*args):
    if len(args)>1:
        d = list(range(len(args)+1))
        d = [d[0],d[2],d[1]] + d[3:]
        return transpose(raw_meshgrid(*args), d)
    else:
        return raw_meshgrid(*args)
