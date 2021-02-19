## Operators:
#  * addidion
#  - substraction
#  * multiplication
#  / division
#  // integer division
#  & reference passthrou (r0)
#  ref reference
#  len length

## Value
#  i dimentional index
#  r register value

import re

def new_ctx():
    from collections import OrderedDict
    ctx = {
        "symbols": OrderedDict(),
        "data": OrderedDict(),
        "cfg": []
    }
    return ctx

def eval_expr(tensor, expr, index=None, pos=0):
    if type(expr) is Functor:
        return expr.eval()
    if not type(expr) is list:
        return expr
    op = expr[pos]
    if op == "+":
        add_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        add_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = add_a + add_b, 1+tks_a+tks_b
    elif op == "-":
        sub_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        sub_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = sub_a - sub_b, 1+tks_a+tks_b
    elif op == "*":
        mul_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        mul_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = mul_a * mul_b, 1+tks_a+tks_b
    elif op == "//":
        idiv_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        idiv_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = idiv_a // idiv_b, 1+tks_a+tks_b
    elif op == "ref":
        ref_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        ref_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        ret = ref_a[ref_b], 1+tks_a+tks_b
    elif op == "i":
        ret = index, 1
    elif op == "&":
        r0 = eval_expr(tensor, ["r0"])
        if tensor.transpose is None:
            t_index = index
        else:
            t_index = [index[tensor.transpose[i]] for i in range(len(index))]
        t_index = tuple(t_index)
        ret = r0[t_index], 1
    elif op == "r":
        ret = tensor.regs, 1
    elif re.match("-?[0-9]+", op):
        ret = int(op), 1
    elif re.match("r[0-9]+", op):
        ret = tensor.regs[int(op[1:])], 1
    elif re.match("i[0-9]+", op):
        ret = index[int(op[1:])], 1
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if type(ret[0]) is Functor:
        ret = ret[0].eval(), ret[1]

    if pos==0:
        return ret[0]
    else:
        return ret

def build_ast(ctx, tensor, expr, transpose=[], recurs=False):
    if not recurs:
        expr = list(expr)

    if tensor.transpose:
        ctx["data"]["trans{}".format("_".join([str(x) for x in tensor.transpose]))] = ("int", tensor.transpose)

    op = expr.pop(0)
    if op == "+":
        add_a = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        add_b = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        return ("+", add_a, add_b)
    elif op == "-":
        sub_a = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        sub_b = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        return ("-", sub_a, sub_b)
    elif op == "*":
        mul_a = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        mul_b = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        return ("*", mul_a, mul_b)
    elif op == "//":
        idiv_a = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        idiv_b = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        return ("//", idiv_a, idiv_b)
    elif op == "ref":
        ref_a = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        ref_b = build_ast(ctx, tensor, expr, transpose=transpose, recurs=True)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        if ref_a == "idx":
            st = ref_b
            for t in [tensor.transpose]+transpose:
                if t:
                    st = ("ref", "trans{}".format("_".join([str(x) for x in t])), st)
            return ("ref", ref_a, st)
        else:
            return ("ref", ref_a, ref_b)
    elif op == "i":
        return "idx"
    elif op == "&":
        r0 = tensor.regs[0]
        r0_cfg = build_ast(ctx, r0, r0.func, transpose=[tensor.transpose]+transpose)
        return r0_cfg
    elif op == "r":
        regs = []
        for r in tensor.regs:
            name = "reg{}".format(id(r))
            ctx["data"][name] = ("float", r)
            regs.append(name)
        name = "reg{}".format(id(tensor.regs))
        ctx["data"][name] = ("float *", regs)
        return name
    elif re.match("-?[0-9]+", op):
        return op
    elif re.match("r[0-9]+", op):
        return tensor.regs[int(op[1:])]
    elif re.match("i[0-9]+", op):
        i = op[1:]
        st = i
        for t in [tensor.transpose]+transpose:
            if t:
                st = ("ref", "trans{}".format("_".join([str(x) for x in t])), st)
        return ("ref","idx",st)
    else:
        raise NotImplementedError("Invalid token {}".format(op))

class Functor():
    def __init__(self, regs, shape, func, transpose=None, offset=None):
        self.regs = regs
        self.shape = shape
        self.func = func
        self.transpose = transpose
        self.offset = offset
        self.type = None
        self.name = None
        self.generated = False

    def __str__(self):
        return "" \
            f"Offset: {self.offset}\n" \
            f"Shape: {self.shape}\n" \
            f"Func: {self.func}\n" \
            f"Regs: {self.regs}\n"

    def __repr__(self):
        return "Tensor: transpose={transpose}, offset={offset}".format(transpose=self.transpose, offset=self.offset)

    def __len__(self):
        return eval_expr(self, self.shape[0])

    def __getitem__(self, idx):
        if idx < len(self):
            regs = [self]
            n = self.shape[1:]
            f = ["&"]
            offset = [idx]+[0]*(len(self.shape)-1)
            return Functor(regs, n, f, offset=offset)
        else:
            raise IndexError()

    def output(self, type, name):
        self.type = type
        self.name = name

    def eval(self):
        import itertools
        import numpy
        shape = list([eval_expr(self, s) for s in self.shape])
        data = []
        for idx in itertools.product(*[range(s) for s in shape]):
            data.append(eval_expr(self, self.func, idx))
        return numpy.array(data).reshape(shape)

    def build_cfg(self, ctx):
        shape  = list([eval_expr(self, s) for s in self.shape])
        if ctx is None:
            ctx = new_ctx()
        ctx["symbols"][self.name] = (self.type, shape)
        ctx["cfg"].append(("for", shape))
        ast = build_ast(ctx, self, self.func)
        ctx["cfg"].append(("=", self, ast))
        ctx["cfg"].append(("endfor",))

        return ctx
