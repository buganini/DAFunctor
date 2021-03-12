def is_number(x):
    if isinstance(x, int):
        return True
    if isinstance(x, float):
        return True
    return False

def is_functor(x):
    from .functor import Functor
    return isinstance(x, Functor)

def is_numpy(x):
    import numpy
    return isinstance(x, numpy.ndarray)
