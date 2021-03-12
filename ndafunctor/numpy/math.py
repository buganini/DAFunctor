from .functor import NumpyFunctor
from ..pytyping import *

def add(a, b):
    def add_with_number(f, n):
        if f._ndaf_src_func is add:
            f.vexpr[1].append(n)
            return f
        else:
            return NumpyFunctor(
                f.shape,
                vexpr=["+", ["v0",n]],
                subs=[f],
                desc="add",
                opdesc="add",
                src_func=add
            )
    if is_number(a) and is_functor(b):
        return add_with_number(b, a)
    elif is_functor(a) and is_number(b):
        return add_with_number(a, b)
    elif is_functor(a) and is_functor(b):
        if tuple(a.shape) != tuple(b.shape):
            raise AssertionError("array shape mismatch")
        if a._ndaf_src_func is add:
            a.vexpr[1].append(f"v{len(a.subs)}")
            a.subs.append(b)
            return  a
        else:
            return NumpyFunctor(
                a.shape,
                vexpr=["+", ["v0","v1"]],
                subs=[a, b],
                desc="add",
                opdesc="add",
                src_func=add
            )
    raise NotImplementedError(f"add({type(a), type(b)})")