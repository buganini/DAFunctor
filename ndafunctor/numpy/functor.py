import math
from ..functor import *

class NumpyFunctor(Functor):
    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            raise NotImplementedError("slice with tuple is not implemented")
        elif isinstance(idx, slice):
            start = idx.start
            stop = idx.stop
            step = idx.step or 1

            raw_start = start
            raw_stop = stop
            while start < 0:
                start += self.shape[0]
            while stop < 0:
                stop += self.shape[0]

            stop = min(stop, self.shape[0])
            base = start

            num = int(math.ceil((stop - start) / step))
            shape = list(self.shape)
            shape[0] = num
            partitions = [(0,s,1) for s in self.shape]
            partitions[0] = (base,num,step)
            iexpr = [f"i{i}" for i in rangel(self.shape)]
            iexpr[0] = ["-", ["i0", base]]
            if step != 1:
                iexpr[0] = ["//", [iexpr[0], step]]
            return NumpyFunctor(
                shape,
                partitions = [partitions],
                iexpr = iexpr,
                subs = [self],
                desc = "{}[{}]".format(self.desc, idx),
                opdesc = f"[{raw_start}:{raw_stop}:{step}]",
            )
        elif isinstance(idx, int):
            if idx < 0:
                idx += self.shape[0]
            if 0 <= idx and idx < len(self):
                shape = list(self.shape[1:])
                partitions = [(0,s,1) for s in self.shape]
                partitions[0] = (idx,1,1)
                iexpr = [f"i{i}" for i in range(1,len(self.shape))]
                return NumpyFunctor(
                    shape,
                    partitions = [partitions],
                    iexpr = iexpr,
                    subs = [self],
                    desc = "{}[{}]".format(self.desc, idx),
                    opdesc = f"[{idx}]",
                )
            else:
                raise IndexError()
        else:
            raise TypeError("Invalid index type")

    def __add__(self, a):
        from .math import add
        return add(self, a)

    def __radd__(self, b):
        from .math import add
        return add(b, self)
