from .tensor import ITensor

def arange(*args):
    if len(args) == 1:
        start = 0
        end = args[0]
        step = 1
    elif len(args) == 2:
        start = args[0]
        end = args[1]
        step = 1
    elif len(args) == 3:
        start = args[0]
        end = args[1]
        step = args[2]
    else:
        raise NotImplementedError("arange")

    regs = [start,end,step]
    n = ["//","-","r1","r0","r2"] # (end - start) // step
    f = ["+","r0","*","i0","r2"] # start + i * step
    return ITensor(regs, [n], f)

def transpose(tensor, dims):
    rmap = [dims.index(i) for i in range(len(tensor.shape))]
    regs = [tensor]
    n = [tensor.shape[dims[i]] for i in range(len(tensor.shape))]
    f = ["&"]
    return ITensor(regs, n, f, transpose=rmap)

def raw_meshgrid(*args):
    regs = args
    n = [len(args)]
    for i in range(len(args)):
        n.append(len(args[i]))
    f = ["ref","ref","r","i0","ref","i","+","i0","1"] # r[i0][i[i0+1]]
    return ITensor(regs, n, f)

def meshgrid(*args):
    if len(args)>1:
        d = list(range(len(args)+1))
        d = [d[0],d[2],d[1]] + d[3:]
        return transpose(raw_meshgrid(*args), d)
    else:
        return raw_meshgrid(*args)
