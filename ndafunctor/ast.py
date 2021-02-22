def strip(expr):
    if type(expr) in (int, float, str):
        return expr
    op = expr[0]
    args = expr[1]
    if op in ("+","-","*","//","/","%"):
        args = [strip(x) for x in args]
        args = [x for x in args if not x is None]
    if not args:
        return None
    if len(args)==1:
        return args[0]
    return [op, args]
