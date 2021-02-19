from .functor import *
from .core import *
from .gen_c import *

def build_cfg(tensors):
    from collections import OrderedDict

    ctx = None
    for t in tensors:
        ctx = t.build_cfg(ctx)

    return ctx
