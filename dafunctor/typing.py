# https://numpy.org/doc/stable/user/basics.types.html

def type_normalize(d):
    if type(d) is int:
        return "i"
    elif type(d) is float:
        return "f"
    elif type(d) is bool:
        return "b"
    elif d == "float":
        return "f"
    elif d in ("i","f","b"):
        return d
    raise TypeError(f"Unsupported type {type(d)}")

def type_reduce(*args):
    rt = None
    for t in args:
        if rt is None:
            rt = t
        elif rt == "i":
            rt = t
    if rt is None:
        raise TypeError(f"Unable to determine type for empty expression")
    return rt

def get_list_type(a):
    ts = [type_normalize(x) for x in a]
    return type_reduce(*ts)

def to_c_type(t):
    tm = {
        "b": "unsigned char",
        "i": "int",
        "f": "float"
    }
    return tm.get(type_normalize(t), t)

def to_struct_type(t):
    tm = {
        "b": "B",
        "i": "i",
        "f": "f"
    }
    return tm.get(type_normalize(t), t)

def to_numpy_type(t):
    import numpy
    tm = {
        "b": numpy.bool,
        "i": numpy.intc,
        "f": numpy.single
    }
    return tm.get(type_normalize(t), t)