def _append(a, b):
    if type(b) is str:
        a.append(b)
        return
    try:
        _ = iter(b)
    except TypeError:
        a.append(b)
    else:
        a.extend(b)

def join(j, a):
    if not a:
        return []
    ret = []
    _append(ret, a[0])
    for e in a[1:]:
        ret.insert(0, j)
        _append(ret, e)
    return ret
