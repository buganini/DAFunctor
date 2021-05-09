from ..functor import Functor, Data, Buffer
from ..typing import *
from ..pytyping import *
from ..common import *
from .functor import NumpyFunctor
from .. import creation, manip
from .manip import *

def array(data):
    return creation.array(NumpyFunctor, data)

def zeros(shape):
    return NumpyFunctor(
        shape,
        vexpr = 0,
        desc = "zeros",
        opdesc = f"zeros({shape})",
    )

def ones(shape):
    return NumpyFunctor(
        shape,
        vexpr = 1,
        desc = "ones",
        opdesc = f"ones({shape})",
    )

def full(shape, fill_value):
    return NumpyFunctor(
        shape,
        vexpr = fill_value,
        desc = "full",
        opdesc = f"full({shape}, {fill_value})",
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

    import math
    data = [start,end,step]
    shape = [int(math.ceil((end - start) / step))]
    return NumpyFunctor(
        shape,
        vexpr = ["+",["d0",["*",["i0","d2"]]]], # start + i * step
        data = data,
        desc = "arange",
        opdesc = f"arange({start}, {end}, {step})",
    )

def raw_meshgrid(*args):
    shape = [len(args)]
    partitions = []
    for i in rangel(args):
        shape.append(len(args[i]))
        rgs = []
        for j in rangel(args):
            rgs.append((0,len(args[j]),1))
        partitions.append(rgs)
    # data[i0][i[i0+1]]
    subs = []
    for i,arg in enumerate(args):
        if is_functor(arg):
            if len(arg.shape) == 1:
                f = arg
                for j in rangel(args)[::-1]:
                    if j < i:
                        f = expand_dims(f, 0)
                    elif j > i:
                        f = expand_dims(f, 1)
                for j in rangel(args):
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
        desc = "raw_meshgrid",
        opdesc = f"raw_meshgrid",
    )

def meshgrid(*args):
    if len(args)>1:
        d = list(range(len(args)+1))
        d = [d[0],d[2],d[1]] + d[3:]
        return manip.transpose(NumpyFunctor, raw_meshgrid(*args), d)
    else:
        return raw_meshgrid(*args)

def frombuffer(buffer, dtype=None):
    if is_buffer(buffer):
        return buffer

    return Buffer(None, dtype, buffer)
