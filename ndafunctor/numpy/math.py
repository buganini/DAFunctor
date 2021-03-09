from .functor import NumpyFunctor
from ..pytyping import *

def add(a, b):
    def add_with_number(f, n):
        if f.src_func is add:
            f.vexpr[1].append(n)
            return f
        else:
            return NumpyFunctor(
                f.shape,
                vexpr=["+", ["v0",n]],
                subs=[f],
                desc="add",
                src_func=add
            )
    if is_number(a) and is_functor(b):
        return add_with_number(b, a)
    elif is_functor(a) and is_number(b):
        return add_with_number(a, b)
    raise NotImplementedError(f"add({type(a), type(b)})")