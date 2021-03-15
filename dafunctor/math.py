from .pytyping import *

def add(cls, a, b):
    def add_with_number(f, n):
        if f._daf_src_func is add:
            f.vexpr[1].append(n)
            return f
        else:
            return cls(
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
        if a._daf_src_func is add:
            a.vexpr[1].append(f"v{len(a.subs)}")
            a.subs.append(b)
            return  a
        else:
            return cls(
                a.shape,
                vexpr=["+", ["v0","v1"]],
                subs=[a, b],
                desc="add",
                opdesc="add",
                src_func=add
            )
    raise NotImplementedError(f"add({type(a), type(b)})")

def subtract(cls, a, b):
    def subtract_with_number(f, n):
        if f._daf_src_func is subtract:
            f.vexpr[1].append(n)
            return f
        else:
            return cls(
                f.shape,
                vexpr=["-", ["v0",n]],
                subs=[f],
                desc="subtract",
                opdesc="subtract",
                src_func=subtract
            )
    if is_number(a) and is_functor(b):
        return cls(
            b.shape,
            vexpr=["-", [a,"v0"]],
            subs=[b],
            desc="subtract",
            opdesc="subtract",
            src_func=subtract
        )
    elif is_functor(a) and is_number(b):
        if a._daf_src_func is subtract:
            a.vexpr[1].append(b)
            return a
        else:
            return cls(
                a.shape,
                vexpr=["-", ["v0",b]],
                subs=[a],
                desc="subtract",
                opdesc="subtract",
                src_func=subtract
            )
    elif is_functor(a) and is_functor(b):
        if tuple(a.shape) != tuple(b.shape):
            raise AssertionError("array shape mismatch")
        if a._daf_src_func is subtract:
            a.vexpr[1].append(f"v{len(a.subs)}")
            a.subs.append(b)
            return  a
        else:
            return cls(
                a.shape,
                vexpr=["+", ["v0","v1"]],
                subs=[a, b],
                desc="subtract",
                opdesc="subtract",
                src_func=subtract
            )
    raise NotImplementedError(f"subtract({type(a), type(b)})")

def multiply(cls, a, b):
    def mul_with_number(f, n):
        if f._daf_src_func is multiply:
            f.vexpr[1].append(n)
            return f
        else:
            return cls(
                f.shape,
                vexpr=["*", ["v0",n]],
                subs=[f],
                desc="multiply",
                opdesc="multiply",
                src_func=multiply
            )
    if is_number(a) and is_functor(b):
        return mul_with_number(b, a)
    elif is_functor(a) and is_number(b):
        return mul_with_number(a, b)
    elif is_functor(a) and is_functor(b):
        if tuple(a.shape) != tuple(b.shape):
            raise AssertionError("array shape mismatch")
        if a._daf_src_func is multiply:
            a.vexpr[1].append(f"v{len(a.subs)}")
            a.subs.append(b)
            return  a
        else:
            return cls(
                a.shape,
                vexpr=["*", ["v0","v1"]],
                subs=[a, b],
                desc="multiply",
                opdesc="multiply",
                src_func=multiply
            )
    raise NotImplementedError(f"multiply({type(a), type(b)})")