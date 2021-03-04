from ..functor import *

class NumpyFunctor(Functor):
    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            pass
        elif isinstance(idx, slice):
            pass
        elif isinstance(idx, int):
            if idx < len(self):
                shape = list(self.shape[1:])
                partitions = [(0,s,1) for s in self.shape]
                partitions[0] = (idx,1,1)
                iexpr = [f"i{i}" for i in range(1,len(self.shape))]
                return Functor(
                    shape,
                    partitions = [partitions],
                    vexpr = "v0",
                    iexpr = iexpr,
                    subs = [self],
                    desc = "{}[{}]".format(self.desc, idx)
                )
            else:
                raise IndexError()
        else:
            raise TypeError("Invalid index type")

