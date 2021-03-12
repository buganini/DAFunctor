import math
from .common import *

def _getitem(cls, a, idx):
    delcnt = 0

    shape = [(0,s,1) for s in a.shape]
    partitions = [(0,s,1) for s in a.shape]
    iexpr = [f"i{i}" for i in rangel(a.shape)]

    for i,s in enumerate(idx):
        if isinstance(s, int):
            shape.pop(i-delcnt)
            partitions[i-delcnt] = (s,1,1)
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

            if not (0 <= start and start < a.shape[i]):
                raise IndexError()

            while stop < 0:
                stop += a.shape[i]

            stop = min(stop, a.shape[i])
            base = start

            num = int(math.ceil((stop - start) / step))
            shape[i-delcnt] = num
            partitions[i] = (base,num,step)
            if base != 0:
                iexpr[i-delcnt] = ["-", [f"i{i}", base]]
            if step != 1:
                iexpr[i-delcnt] = ["//", [iexpr[i-delcnt], step]]
        else:
            raise TypeError("Invalid index type")
    return cls(
        shape,
        partitions = [partitions],
        iexpr = iexpr,
        subs = [a],
        desc = "{}[{}]".format(a.desc, idx),
        opdesc = f"[{idx}]",
    )

def getitem(cls, a, idx):
    if isinstance(idx, tuple):
        return _getitem(cls, a, idx)
    elif isinstance(idx, slice):
        return _getitem(cls, a, tuple([idx]))
    elif isinstance(idx, int):
        return _getitem(cls, a, tuple([idx]))
    else:
        raise TypeError("Invalid index type")