from .functor import *
from .gen_c import *
from .decorator import *
from .pytyping import is_functor

def build_cfg(tensors):
    from collections import OrderedDict

    ctx = None
    for t in tensors:
        ctx = t.build_cfg(ctx)

    return ctx
