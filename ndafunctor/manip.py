import math
from .common import *

def getitem(cls, a, idx):
    if isinstance(idx, tuple):
        raise NotImplementedError("slice with tuple is not implemented")
    elif isinstance(idx, slice):
        start = idx.start
        stop = idx.stop
        step = idx.step or 1

        raw_start = start
        raw_stop = stop
        while start < 0:
            start += a.shape[0]
        while stop < 0:
            stop += a.shape[0]

        stop = min(stop, a.shape[0])
        base = start

        num = int(math.ceil((stop - start) / step))
        shape = list(a.shape)
        shape[0] = num
        partitions = [(0,s,1) for s in a.shape]
        partitions[0] = (base,num,step)
        iexpr = [f"i{i}" for i in rangel(a.shape)]
        iexpr[0] = ["-", ["i0", base]]
        if step != 1:
            iexpr[0] = ["//", [iexpr[0], step]]
        return cls(
            shape,
            partitions = [partitions],
            iexpr = iexpr,
            subs = [a],
            desc = "{}[{}]".format(a.desc, idx),
            opdesc = f"[{raw_start}:{raw_stop}:{step}]",
        )
    elif isinstance(idx, int):
        if idx < 0:
            idx += a.shape[0]
        if 0 <= idx and idx < len(a):
            shape = list(a.shape[1:])
            partitions = [(0,s,1) for s in a.shape]
            partitions[0] = (idx,1,1)
            iexpr = [f"i{i}" for i in range(1,len(a.shape))]
            return cls(
                shape,
                partitions = [partitions],
                iexpr = iexpr,
                subs = [a],
                desc = "{}[{}]".format(a.desc, idx),
                opdesc = f"[{idx}]",
            )
        else:
            raise IndexError()
    else:
        raise TypeError("Invalid index type")