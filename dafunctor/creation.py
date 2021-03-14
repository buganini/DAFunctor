from .pytyping import *
from .common import *
from .functor import Data
from .ast import strip as ast_strip

def _shape(data):
    try:
        _ = iter(data)
    except TypeError:
        return tuple()
    else:
        homo = True
        shape = [_shape(e) for e in data]
        for s in shape[1:]:
            if s is None:
                homo = False
            if s != shape[0]:
                homo = False
        if homo:
            return tuple([len(shape), *shape[0]])
        else:
            return None

def _flatten(data):
    ret = []
    todo = data
    while todo:
        e = todo.pop(0)
        try:
            _ = iter(e)
        except TypeError:
            ret.append(e)
        else:
            todo.extend(e)
    return ret

def array(cls, data):
    if is_functor(data):
        return data
    shape = _shape(data)
    if shape is None:
        raise ValueError("Heterogeneous array is not supported")
    vexpr = ast_strip(["+", [
        ["*",
            [f"i{i}"]
            +
            [shape[j] for j in range(i+1, len(shape))]
        ]
        for i in rangel(shape)
    ]])
    return cls(
        shape,
        vexpr = ["ref", ["d", vexpr]],
        data = Data(_flatten(data), "array"),
        desc = f"array({str(shape)})",
        opdesc = f"array()",
    )
