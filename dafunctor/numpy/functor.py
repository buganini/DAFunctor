import math
from ..functor import *
from .. import manip

class NumpyFunctor(Functor):
    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        return manip.getitem(NumpyFunctor, self, idx)

    def __setitem__(self, idx, value):
        return manip.setitem(NumpyFunctor, self, idx, value)

    def __add__(self, a):
        from .math import add
        return add(self, a)

    def __radd__(self, b):
        from .math import add
        return add(b, self)
