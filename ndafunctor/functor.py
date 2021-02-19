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
#  d data value

import re

def new_ctx():
    from collections import OrderedDict
    ctx = {
        "symbols": OrderedDict(),
        "data": OrderedDict(),
        "cfg": []
    }
    return ctx

class Expr():
    def __init__(self, expr):
        self.expr = expr
        self.pos = 0

    def take(self):
        try:
            ret = self.expr[self.pos]
            self.pos += 1
            return ret
        except:
            raise IndexError("Index out of ", self.expr)

    def dump(self):
        print(self.expr[:self.pos], "<cursor>", self.expr[self.pos:])

def eval_expr(tensor, expr, index=None):
    if type(expr) is Functor:
        return expr.eval()

    if not type(expr) is Expr:
        return expr

    op = expr.take()
    if op == "+":
        add_a = eval_expr(tensor, expr, index)
        add_b = eval_expr(tensor, expr, index)
        ret = add_a + add_b
    elif op == "-":
        sub_a = eval_expr(tensor, expr, index)
        sub_b = eval_expr(tensor, expr, index)
        ret = sub_a - sub_b
    elif op == "*":
        mul_a = eval_expr(tensor, expr, index)
        mul_b = eval_expr(tensor, expr, index)
        ret = mul_a * mul_b
    elif op == "//":
        idiv_a = eval_expr(tensor, expr, index)
        idiv_b = eval_expr(tensor, expr, index)
        ret = idiv_a // idiv_b
    elif op == "ref":
        ref_a = eval_expr(tensor, expr, index)
        ref_b = eval_expr(tensor, expr, index)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        ret = ref_a[ref_b]
    elif op == "i":
        ret = index
    elif op == "&":
        r0 = eval_expr(tensor, ["r0"])
        if tensor.transpose is None:
            t_index = index
        else:
            t_index = [index[tensor.transpose[i]] for i in range(len(index))]
        t_index = tuple(t_index)
        ret = r0[t_index]
    elif op == "r":
        ret = tensor.regs
    elif re.match("-?[0-9]+", op):
        ret = int(op)
    elif re.match("d[0-9]+", op):
        ret = tensor.data[int(op[1:])]
    elif re.match("i[0-9]+", op):
        ret = index[int(op[1:])]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if type(ret) is Functor:
        ret = ret.eval()

    return ret

def build_ast(ctx, tensor, expr, transpose=[], recurs=False):
    op = expr.take()
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
        return ("ref", ref_a, ref_b)
    elif op == "i":
        return ("term","idx")
    elif op == "&":
        r0 = tensor.regs[0]
        r0_cfg = build_ast(ctx, r0, r0.func, transpose=[tensor.transpose]+transpose)
        return r0_cfg
    elif op == "d":
        regs = []
        for r in tensor.regs:
            name = "data{}".format(id(r))
            ctx["data"][name] = ("float", r)
            regs.append(name)
        name = "data{}".format(id(tensor.regs))
        ctx["data"][name] = ("float *", regs)
        return name
    elif re.match("-?[0-9]+", op):
        return ("term",op)
    elif re.match("d[0-9]+", op):
        return ("term", str(tensor.data[int(op[1:])]))
    elif re.match("i[0-9]+", op):
        return ("idx", op[1:])
    else:
        raise NotImplementedError("Invalid token {}".format(op))

class Functor():
    def __init__(self, shape, dtype=None, dexpr=None, iexpr=None, data=None, subs=None, desc=None):
        # external perspective
        self.shape = shape
        self.dtype = dtype
        self.desc = desc

        # internal perspective
        self.dexpr = dexpr # data expression
        self.iexpr = iexpr # index expression
        self.data = data # static data
        self.subs = subs # sub functors

        # runtime
        self.name = None
        self.generated = False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Functor(desc={desc} shape={shape})".format(desc=self.desc, shape=self.shape)

    def __len__(self):
        return self.shape[0]

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
        data = []
        for idx in itertools.product(*[range(s) for s in self.shape]):
            data.append(eval_expr(self, Expr(self.dexpr), idx))
        return numpy.array(data).reshape(self.shape)

    def build_cfg(self, ctx):
        shape  = list([eval_expr(self, s) for s in self.shape])
        if ctx is None:
            ctx = new_ctx()
        ctx["symbols"][self.name] = (self.type, shape)
        ctx["cfg"].append(("for", shape))
        ast = build_ast(ctx, self, Expr(self.dexpr))
        ctx["cfg"].append(("=", self, ast))
        ctx["cfg"].append(("endfor",))

        return ctx
