import math
from ..functor import *
from .. import manip

class TorchFunctor(Functor):
    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        return manip.getitem(TorchFunctor, self, idx)

    def __setitem__(self, idx, value):
        return manip.setitem(TorchFunctor, self, idx, value)

    def size(self):
        return tuple(self.shape)

    def permute(self, axis):
        return manip.transpose(TorchFunctor, self, axis)