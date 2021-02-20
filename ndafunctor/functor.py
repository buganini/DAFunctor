## Operators:
#  * addidion
#  - substraction
#  * multiplication
#  / division
#  // integer division
#  ref reference

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

def eval_expr(functor, expr, index=None):
    if type(expr) is Functor:
        return expr.eval()

    if not type(expr) is Expr:
        return expr

    op = expr.take()
    if op == "+":
        add_a = eval_expr(functor, expr, index)
        add_b = eval_expr(functor, expr, index)
        ret = add_a + add_b
    elif op == "-":
        sub_a = eval_expr(functor, expr, index)
        sub_b = eval_expr(functor, expr, index)
        ret = sub_a - sub_b
    elif op == "*":
        mul_a = eval_expr(functor, expr, index)
        mul_b = eval_expr(functor, expr, index)
        ret = mul_a * mul_b
    elif op == "//":
        idiv_a = eval_expr(functor, expr, index)
        idiv_b = eval_expr(functor, expr, index)
        ret = idiv_a // idiv_b
    elif op == "ref":
        ref_a = eval_expr(functor, expr, index)
        ref_b = eval_expr(functor, expr, index)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        # print("ref_a", ref_a)
        # print("ref_b", ref_b)
        ret = ref_a[ref_b]
    elif op == "d":
        ret = functor.data
    elif op == "s":
        n = eval_expr(functor, expr, index)
        ret = functor.subs[n]
        # print(ret)
    elif re.match("-?[0-9]+", op):
        ret = int(op)
    elif re.match("d[0-9]+", op):
        ret = functor.data[int(op[1:])]
    elif re.match("i[0-9]+", op):
        # print(op)
        ret = index[int(op[1:])]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if type(ret) is Functor:
        ret = ret.eval()

    return ret

def build_ast(ctx, functor, expr, idx_level=0):
    op = expr.take()
    if op == "+":
        add_a = build_ast(ctx, functor, expr)
        add_b = build_ast(ctx, functor, expr)
        return ("+", add_a, add_b)
    elif op == "-":
        sub_a = build_ast(ctx, functor, expr)
        sub_b = build_ast(ctx, functor, expr)
        return ("-", sub_a, sub_b)
    elif op == "*":
        mul_a = build_ast(ctx, functor, expr)
        mul_b = build_ast(ctx, functor, expr)
        return ("*", mul_a, mul_b)
    elif op == "//":
        idiv_a = build_ast(ctx, functor, expr)
        idiv_b = build_ast(ctx, functor, expr)
        return ("//", idiv_a, idiv_b)
    elif op == "ref":
        ref_a = build_ast(ctx, functor, expr)
        ref_b = build_ast(ctx, functor, expr)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        return ("ref", ref_a, ref_b)
    elif op == "d":
        data = []
        for r in functor.data:
            name = "data{}".format(id(r))
            ctx["data"][name] = ("float", r)
            data.append(name)
        name = "data{}".format(id(functor.data))
        ctx["data"][name] = ("float *", data)
        return name
    elif re.match("-?[0-9]+", op):
        return ("term",op)
    elif re.match("d[0-9]+", op):
        return ("term", str(functor.data[int(op[1:])]))
    elif re.match("i[0-9]+", op):
        return ("idx", op[1:], idx_level)
    else:
        raise NotImplementedError("Invalid token {}".format(op))

class Shape():
    def __init__(self, shape):
        self.shape = self.ensure_list(shape)

    def slices(self):
        import itertools
        ret = []
        for axis_slices in self.shape:
            dslices = []
            b = 0
            for e in axis_slices:
                dslices.append((b,e-b))
                b = e
            ret.append(dslices)
        return list(itertools.product(*ret))

    def __str__(self):
        return str(self.shape)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.shape)

    def __getitem__(self, idx):
        return [x[-1] for x in self.shape][idx]

    def composite(self, shape):
        shape = self.ensure_list(shape)
        ret = []
        for i in range(len(self.shape)):
            ret.append(sorted(list(set(self.shape[i] + shape[i]))))
        return Shape(ret)

    def ensure_list(self, shape):
        if type(shape) is Shape:
            return shape.shape
        ret = []
        for s in shape:
            if type(s) is int:
                ret.append([s])
            else:
                ret.append(list(s))
        return ret

class Functor():
    def __init__(self, shape, dtype=None, dexpr=None, iexpr=None, data=None, subs=None, desc=None):
        # external perspective
        self.shape = Shape(shape)
        self.dtype = dtype
        self.desc = desc

        # internal perspective
        self.dexpr = dexpr # data expression, evaluate to value
        self.iexpr = iexpr # index expression, evaluate from external index to internal index
        self.data = data # static data
        self.subs = subs # sub functors

        # runtime
        self.name = None
        self.generated = False
        self.eval_cached = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        d = []
        d.append("desc={}".format(self.desc))
        d.append("shape={}".format(self.shape))
        if self.iexpr:
            d.append("iexpr={}".format(self.iexpr))
        if self.subs:
            d.append("subs={}".format(len(self.subs)))
        return "Functor({})".format(", ".join(d))

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

    def print(self, indent=0, suffix=""):
        indent__num = 4
        print(" "*indent*indent__num, end="")
        print("Functor{}:".format(suffix))

        print(" "*(indent+1)*indent__num, end="")
        print("{}".format(self.desc))

        print(" "*(indent+1)*indent__num, end="")
        print("shape={}".format(self.shape))

        print(" "*(indent+1)*indent__num, end="")
        print("dexpr={}".format(self.dexpr))

        print(" "*(indent+1)*indent__num, end="")
        print("iexpr={}".format(self.iexpr))

        for i,s in enumerate(self.subs or []):
            s.print(indent+1, suffix="[{}]".format(i))


    def output(self, type, name):
        self.type = type
        self.name = name

    def eval_index(self, index):
        if self.iexpr is None:
            return index
        else:
            return tuple([
                eval_expr(self, Expr(iexpr), index)
                for iexpr in self.iexpr
            ])

    def eval(self):
        if self.eval_cached is None:
            import itertools
            import numpy
            data = []
            if self.dexpr:
                for idx in itertools.product(*[range(b,b+n) for b,n in self.shape.slices()[0]]):
                    data.append(eval_expr(self, Expr(self.dexpr), self.eval_index(idx)))
            else:
                for i,slice in enumerate(self.shape.slices()):
                    for idx in itertools.product(*[range(b,b+n) for b,n in slice]):
                        functor = self.subs[i]
                        sub_idx = self.eval_index(idx)
                        # sub_idx = functor.eval_index(sub_idx)
                        # print("self", self)
                        # print("functor", functor)
                        # print("eval", functor.eval())
                        # print("idx", idx)
                        # print("shape", functor.shape)
                        # print("sub_idx",sub_idx)
                        # print("tran_sub_idx",sub_idx)
                        data.append(functor.eval()[sub_idx])
            # print("eval", self.desc)
            # print(data)
            # print("============")
            self.eval_cached = numpy.array(data).reshape(self.shape)
        return self.eval_cached

    def build_idx(self, ctx, idx_level=0):
        if self.iexpr is None:
            return idx_level
        else:
            idx_level += 1
            # for iexpr in self.iexpr:
                # ctx["defines"].append()
            return idx_level
    def build_cfg(self, ctx):
        shape  = list([eval_expr(self, s) for s in self.shape])
        if ctx is None:
            ctx = new_ctx()
        ctx["symbols"][self.name] = (self.type, shape)
        ctx["cfg"].append(("for", shape))
        ast = build_ast(ctx, self, Expr(self.dexpr), self.build_idx(ctx))
        ctx["cfg"].append(("=", self, ast))
        ctx["cfg"].append(("endfor",))

        return ctx
