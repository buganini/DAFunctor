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

    def __sub__(self, a):
        from .math import subtract
        return subtract(self, a)

    def __rsub__(self, b):
        from .math import subtract
        return subtract(b, self)

    def __add__(self, a):
        from .math import add
        return add(self, a)

    def __radd__(self, b):
        from .math import add
        return add(b, self)

    def __mul__(self, a):
        from .math import multiply
        return multiply(self, a)

    def __rmul__(self, b):
        from .math import multiply
        return multiply(b, self)

    def __gt__(self, a):
        from .logic import greater
        return greater(self, a)
