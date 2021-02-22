from .functor import Functor, Data
from .manipulation import *

def _shape(data):
    try:
        _ = iter(data)
    except TypeError:
        return tuple()
    else:
        homo = True
        shape = [_shape(e) for e in data]
        for s in shape[1:]:
            if s is None:
                homo = False
            if s != shape[0]:
                homo = False
        if homo:
            return tuple([len(shape), *shape[0]])
        else:
            return None

def _flatten(data):
    ret = []
    todo = data
    while todo:
        e = todo.pop(0)
        try:
            _ = iter(e)
        except TypeError:
            ret.append(e)
        else:
            todo.extend(e)
    return ret

def array(data):
    shape = _shape(data)
    if shape is None:
        raise ValueError("Heterogeneous array is not supported")
    dexpr = ["+", [
        ["*",
            [f"i{i}"]
            +
            [shape[j] for j in range(i+1, len(shape))]
        ]
        for i in range(len(shape))
    ]]
    return Functor(
        shape,
        dexpr = ["ref", ["d", dexpr]],
        data = Data(_flatten(data), "array"),
        desc = f"array({str(shape)})"
    )

def zeros(shape):
    return Functor(
        shape,
        dexpr = 0,
        desc = "zeros"
    )

def ones(shape):
    return Functor(
        shape,
        dexpr = 1,
        desc = "ones"
    )

def full(shape, fill_value):
    return Functor(
        shape,
        dexpr = fill_value,
        desc = "full"
    )

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
        dexpr = ["+",["d0",["*",["i0","d2"]]]], # start + i * step
        data = data,
        desc = "arange"
    )

def raw_meshgrid(*args):
    shape = [range(0,len(args)+1)]
    for i in range(len(args)):
        shape.append(len(args[i]))
    # data[i0][i[i0+1]]
    subs = []
    for i in range(len(args)):
        subs.append(Functor(
            shape[1:],
            dexpr = ["ref",["d",f"i{i}"]], # data[i{i0+1}]]
            data = Data(args[i], "meshgrid"),
            desc = f"raw_meshgrid[{i}]"
        ))
    iexpr = [0]
    for i in range(len(shape)-1):
        iexpr.append(f"i{i}")
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
