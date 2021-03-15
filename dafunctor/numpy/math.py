from .functor import NumpyFunctor
from .. import math

def add(a, b):
    return math.add(NumpyFunctor, a, b)

def subtract(a, b):
    return math.subtract(NumpyFunctor, a, b)

def multiply(a, b):
    return math.multiply(NumpyFunctor, a, b)
