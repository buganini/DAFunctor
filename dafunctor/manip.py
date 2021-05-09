import math
from .functor import Functor
from .expression import ast_strip
from .common import *

def clone(cls, a):
    f = cls(
        a.shape,
        partitions = a.partitions,
        dtype = a.dtype,
        vexpr = a.vexpr,
        iexpr = a.iexpr,
        sexpr = a.sexpr,
        data = a.data,
        subs = a.subs,
        desc = a.desc,
        opdesc = a.opdesc,
        name = a.name,
        buffer = a.buffer,
        src_func = a._daf_src_func,
        is_contiguous = a._daf_is_contiguous,
    )
    return f

def transpose(cls, functor, dims):
    iexpr = [f"i{axis}" for axis in dims]
    shape = [functor.shape[dims[i]] for i in rangel(functor.shape)]
    return cls(
        shape,
        partitions = [[(0,s,1) for s in functor.shape]],
        iexpr = iexpr,
        desc = f"transposed_{functor.desc}",
        opdesc = f"transpose({dims})",
        subs = [functor]
    )

def reshape(cls, a, shape):
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
    return cls(
        shape,
        partitions = [[(0,s,1) for s in a.shape]],
        iexpr = iexpr,
        desc = f"reshape({shape})_{a.desc}",
        opdesc = f"reshape({shape})",
        subs = [a],
        src_func = reshape,
        # is_contiguous = a._daf_is_contiguous
    )

def _getitem(cls, a, idx):
    delcnt = 0

    shape = [(0,s,1) for s in a.shape]
    partitions = [(0,s,1) for s in a.shape]
    iexpr = [f"i{i}" for i in rangel(a.shape)]

    for i,s in enumerate(idx):
        if isinstance(s, int):
            if s < 0:
                s += a.shape[i]

            if s < 0 or s >= a.shape[i]:
                raise IndexError()

            shape.pop(i-delcnt)
            partitions[i] = (s,1,1)
            iexpr.pop(i-delcnt)
            delcnt += 1
        elif isinstance(s, slice):
            start = s.start
            stop = s.stop
            step = s.step or 1

            if start is None:
                start = 0
            if stop is None:
                stop = a.shape[i]

            if start < 0:
                start += a.shape[i]

            while stop < 0:
                stop += a.shape[i]

            stop = min(stop, a.shape[i])

            num = int(math.ceil((stop - start) / step))
            shape[i-delcnt] = num
            partitions[i] = (start,num,step)
            if start != 0:
                iexpr[i-delcnt] = ["-", [f"i{i}", start]]
            if step != 1:
                iexpr[i-delcnt] = ["//", [iexpr[i-delcnt], step]]
        else:
            raise TypeError("Invalid index type")
    f = cls(
        shape,
        partitions = [partitions],
        iexpr = iexpr,
        subs = [a],
        desc = "{}[{}]".format(a.desc, idx),
        opdesc = f"[{idx}]",
    )
    return f

def getitem(cls, a, idx):
    if isinstance(idx, tuple):
        return _getitem(cls, a, idx)
    elif isinstance(idx, slice):
        return _getitem(cls, a, tuple([idx]))
    elif isinstance(idx, int):
        return _getitem(cls, a, tuple([idx]))
    else:
        raise TypeError("Invalid index type")

def _setitem(cls, a, idx, value):
    f = clone(cls, a)
    delcnt = 0

    vshape = [(0,s,1) for s in a.shape]
    vcnt = 0
    viexpr = []
    modify = []
    constraints = []
    partitions = []
    subs = []

    for i,s in enumerate(idx):
        if isinstance(s, int):
            vshape.pop(i-delcnt)
            viexpr.append(s)

            start = s
            num = 1
            step = 1

            if s == 0:
                before = None
            else:
                before = (0, s, 1)
            if a.shape[i]-(s+1) == 0:
                after = None
            else:
                after = (s+1, a.shape[i]-(s+1), 1)

            delcnt += 1
        elif isinstance(s, slice):
            start = s.start
            stop = s.stop
            step = s.step or 1

            if start is None:
                start = 0
            if stop is None:
                stop = a.shape[i]

            if start < 0:
                start += a.shape[i]

            while stop < 0:
                stop += a.shape[i]

            stop = min(stop, a.shape[i])

            num = int(math.ceil((stop - start) / step))
            vshape[i-delcnt] = (0,num,1)

            viexpr.append(["+",[start, ["*", [f"i{vcnt}", step]]]])
            vcnt += 1

            if s == 0:
                before = None
            else:
                before = (0, start, 1)
            if a.shape[i]-(stop) == 0:
                after = None
            else:
                after = (stop, a.shape[i]-(stop), 1)
        else:
            raise TypeError("Invalid index type")

        if before:
            partitions.append(constraints + [before] + [(0,x,1) for x in a.shape[i+1:]])
            subs.append(f)
        if after:
            partitions.append(constraints + [after] + [(0,x,1) for x in a.shape[i+1:]])
            subs.append(f)

        while len(viexpr) < len(a.shape):
            viexpr.append(f"i{vcnt}")
            vcnt += 1

        constraints.append((start, num, step))

    partitions.append(constraints + [(0,x,1) for x in a.shape[len(constraints):]])
    if not isinstance(value, Functor):
        value = cls(
            [x[1] for x in vshape],
            vexpr = value,
            desc = f"constant({value})",
            opdesc = f"constant({value})",
        )
    value = cls(
        a.shape,
        partitions = [[(0,x[1],1) for x in vshape]],
        iexpr = viexpr,
        subs = [value],
        desc = f"shift",
        opdesc = f"shift",
    )
    subs.append(value)

    a.iexpr = None
    a.vexpr = None
    a.sexpr = None
    a.partitions = partitions
    a.subs = subs
    a.desc = "assign_{}[{}]".format(a.desc, idx)
    a.opdesc = f"assign [{idx}]"

def setitem(cls, a, idx, value):
    if isinstance(idx, tuple):
        _setitem(cls, a, idx, value)
    elif isinstance(idx, slice):
        _setitem(cls, a, tuple([idx]), value)
    elif isinstance(idx, int):
        _setitem(cls, a, tuple([idx]), value)
    else:
        raise TypeError("Invalid index type")
