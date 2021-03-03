from ..functor import Functor, Data
from .functor import NumpyFunctor
from ..ast import strip as ast_strip
import functools

def transpose(functor, dims):
    iexpr = [f"i{axis}" for axis in dims]
    shape = [functor.shape[dims[i]] for i in range(len(functor.shape))]
    return NumpyFunctor(
        shape,
        iexpr = iexpr,
        desc = f"transposed_{functor.desc}",
        subs = [functor]
    )

def reshape(a, shape):
    offset = ["+",[
        ["*",
            [f"i{i}"] + [a.shape[j] for j in range(i+1,len(a.shape))]
        ]
        for i in range(len(a.shape))
    ]]
    iexpr = []
    for i in range(len(shape)):
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
        iexpr = iexpr,
        desc = f"reshape({shape})_{a.desc}",
        subs = [a]
    )

def stack(array, axis=0):
    if axis < 0:
        axis = len(array[0].shape) + axis
    iexpr = [f"i{i}" for i in range(len(array[0].shape))]
    iexpr.insert(axis, 0)
    shape = list(array[0].shape)
    shape.insert(axis, len(array))
    ranges = []
    for i in range(len(array)):
        rgs = [(0,s,1) for s in shape]
        rgs[axis] = (i,1,1)
        ranges.append(rgs)
    return NumpyFunctor(
        shape,
        ranges = ranges,
        iexpr = iexpr,
        desc = f"stack_{axis}",
        subs = array
    )

def concatenate(array, axis=0):
    iexpr = [f"i{i}" for i in range(len(array[0].shape))]
    shape = list(array[0].shape)
    orig_shape = shape[axis]
    shape[axis] *= len(array)
    ranges = []
    for i in range(len(array)):
        rgs = [(0,s,1) for s in shape]
        rgs[axis] = (i*orig_shape,orig_shape,1)
        ranges.append(rgs)
    return NumpyFunctor(
        shape,
        ranges = ranges,
        iexpr = iexpr,
        desc = "concatenate",
        subs = array
    )

def expand_dims(a, axis):
    iexpr = [f"i{i}" for i in range(len(a.shape))]
    iexpr.insert(axis, 0)
    shape = list(a.shape)
    shape.insert(axis, 1)
    return NumpyFunctor(
        shape,
        iexpr = iexpr,
        desc = f"expand_dims_{axis}_{a.desc}",
        subs = [a]
    )

def repeat(a, repeats, axis=None):
    if isinstance(a, Functor):
        if axis is None:
            sz = functools.reduce(lambda x,y:x*y, a.shape)
            flt = reshape(a, [sz])

            shape = [sz*repeats]
            iexpr = [["*", [f"i0", repeats]]]
            sexpr = (0, 0, repeats, 1)
            return NumpyFunctor(
                shape,
                iexpr = iexpr,
                sexpr = sexpr,
                desc = f"repeat_{repeats}",
                subs = [flt]
            )
        else:
            shape = list(a.shape)
            shape[axis] *= repeats
            iexpr = [f"i{i}" for i in range(len(shape))]
            iexpr[axis] = ["*", [f"i{axis}", repeats]]
            sexpr = (axis, 0, repeats, 1)
            return NumpyFunctor(
                shape,
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
            dexpr = a
        )
