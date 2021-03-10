from ..functor import Functor, Data
from ..common import *
from .functor import NumpyFunctor
from ..pytyping import *
from ..ast import strip as ast_strip
import functools

def ascontiguousarray(a):
    r = NumpyFunctor(
        a.shape,
        vexpr = "v0",
        subs = [a],
        desc = "ascontiguousarray"
    )
    r._ndaf_requested_contiguous = True
    return r


def transpose(functor, dims):
    iexpr = [f"i{axis}" for axis in dims]
    shape = [functor.shape[dims[i]] for i in rangel(functor.shape)]
    return NumpyFunctor(
        shape,
        partitions = [[(0,s,1) for s in functor.shape]],
        iexpr = iexpr,
        desc = f"transposed_{functor.desc}",
        subs = [functor]
    )

def reshape(a, shape):
    offset = ["+",[
        ["*",
            [f"i{i}"] + [a.shape[j] for j in range(i+1,len(a.shape))]
        ]
        for i in rangel(a.shape)
    ]]
    iexpr = []
    for i in rangel(shape):
        iexpr.append(
            ast_strip([
                "//",
                [
                    ["%",
                        [offset]+[
                            [
                                "*",
                                shape[j:]
                            ]
                            for j in range(i+1)
                        ]
                    ],
                    ["*", shape[i+1:]]
                ]
            ])
        )
    return NumpyFunctor(
        shape,
        partitions = [[(0,s,1) for s in a.shape]],
        iexpr = iexpr,
        desc = f"reshape({shape})_{a.desc}",
        subs = [a]
    )

def stack(array, axis=0):
    if axis < 0:
        axis = len(array[0].shape) + axis
    iexpr = [f"i{i}" for i in rangel(array[0].shape)]
    iexpr.insert(axis, "si")
    shape = list(array[0].shape)
    shape.insert(axis, len(array))
    partitions = []
    for i in rangel(array):
        rgs = [(0,s,1) for s in array[i].shape]
        partitions.append(rgs)
    return NumpyFunctor(
        shape,
        partitions = partitions,
        iexpr = iexpr,
        desc = f"stack_{axis}",
        subs = array
    )

def concatenate(array, axis=0):
    ashape = list(array[0].shape)
    orig_shape = ashape[axis]

    iexpr = [f"i{i}" for i in rangel(ashape)]
    iexpr[axis] = ["+", [f"i{axis}", ["*", ["si", orig_shape]]]]

    shape = list(ashape)
    shape[axis] *= len(array)
    partitions = []
    for i in rangel(array):
        rgs = [(0, s, 1) for s in ashape]
        partitions.append(rgs)
    return NumpyFunctor(
        shape,
        partitions = partitions,
        iexpr = iexpr,
        desc = "concatenate",
        subs = array
    )

def expand_dims(a, axis):
    iexpr = [f"i{i}" for i in rangel(a.shape)]
    iexpr.insert(axis, 0)
    shape = list(a.shape)
    shape.insert(axis, 1)
    return NumpyFunctor(
        shape,
        partitions = [[(0,s,1) for s in a.shape]],
        iexpr = iexpr,
        desc = f"expand_dims_{axis}_{a.desc}",
        subs = [a]
    )

def repeat(a, repeats, axis=None):
    if is_functor(a):
        if axis is None:
            sz = functools.reduce(lambda x,y:x*y, a.shape)
            flt = reshape(a, [sz])

            shape = [sz*repeats]
            iexpr = [["*", [f"i0", repeats]]]
            sexpr = (0, 0, repeats, 1)
            return NumpyFunctor(
                shape,
                partitions = [[(0,sz,1)]],
                iexpr = iexpr,
                sexpr = sexpr,
                desc = f"repeat_{repeats}",
                subs = [flt]
            )
        else:
            shape = list(a.shape)
            shape[axis] *= repeats
            iexpr = [f"i{i}" for i in rangel(shape)]
            iexpr[axis] = ["*", [f"i{axis}", repeats]]
            sexpr = (axis, 0, repeats, 1)
            return NumpyFunctor(
                shape,
                partitions = [[(0,s,1) for s in a.shape]],
                iexpr = iexpr,
                sexpr = sexpr,
                desc = f"repeat_{repeats}",
                subs = [a]
            )
    else:
        shape = [repeats]
        return NumpyFunctor(
            shape,
            desc = f"repeat_{repeats}",
            vexpr = a
        )
