from ..functor import Functor, Data, Buffer
from ..typing import *
from .functor import NumpyFunctor
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
    if isinstance(data, Functor):
        return data
    shape = _shape(data)
    if shape is None:
        raise ValueError("Heterogeneous array is not supported")
    vexpr = ast_strip(["+", [
        ["*",
            [f"i{i}"]
            +
            [shape[j] for j in range(i+1, len(shape))]
        ]
        for i in range(len(shape))
    ]])
    return NumpyFunctor(
        shape,
        vexpr = ["ref", ["d", vexpr]],
        data = Data(_flatten(data), "array"),
        desc = f"array({str(shape)})"
    )

def zeros(shape):
    return NumpyFunctor(
        shape,
        vexpr = 0,
        desc = "zeros"
    )

def ones(shape):
    return NumpyFunctor(
        shape,
        vexpr = 1,
        desc = "ones"
    )

def full(shape, fill_value):
    return NumpyFunctor(
        shape,
        vexpr = fill_value,
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
    return NumpyFunctor(
        shape,
        vexpr = ["+",["d0",["*",["i0","d2"]]]], # start + i * step
        data = data,
        desc = "arange"
    )

def raw_meshgrid(*args):
    shape = [len(args)]
    partitions = []
    for i in range(len(args)):
        shape.append(len(args[i]))
        rgs = []
        for j in range(len(args)):
            rgs.append((0,len(args[j]),1))
        partitions.append(rgs)
    # data[i0][i[i0+1]]
    subs = []
    for i,arg in enumerate(args):
        if isinstance(arg, Functor):
            if len(arg.shape) == 1:
                f = arg
                for j in range(len(args))[::-1]:
                    if j < i:
                        f = expand_dims(f, 0)
                    elif j > i:
                        f = expand_dims(f, 1)
                for j in range(len(args)):
                    if j != i:
                        f = repeat(f, len(args[j]), j)
                subs.append(f)
            else:
                raise ValueError("meshgrid only accept 1-D array inputs")
        else:
            subs.append(NumpyFunctor(
                shape[1:],
                vexpr = ["ref",["d",f"i{i}"]], # data[i{i0+1}]]
                data = Data(arg, "meshgrid"),
                desc = f"raw_meshgrid[{i}]"
            ))
    iexpr = ["si"]
    for i in range(len(shape)-1):
        iexpr.append(f"i{i}")
    return NumpyFunctor(
        shape,
        partitions = partitions,
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

def frombuffer(buffer, dtype=None):
    if isinstance(buffer, Buffer):
        return buffer

    return Buffer(None, dtype, buffer)
