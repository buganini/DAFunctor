from .functor import TorchFunctor
from .. import creation

def Tensor(data):
    return creation.array(TorchFunctor, data)
