from .functor import NumpyFunctor
from .. import logic

def greater(a, b):
    return logic.greater(NumpyFunctor, a, b)