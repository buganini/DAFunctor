## Operators:
#  * addidion
#  - substraction
#  * multiplication
#  / division
#  // integer division
#  ref reference

## Value
#  i{n} index on n-th axis
#  f{n} n-th sub-functor
#  d data value

import re

def new_ctx():
    from collections import OrderedDict
    ctx = {
        "symbols": OrderedDict(),
        "data": OrderedDict(),
        "stmt": [],
    }
    return ctx

class Expr():
    def __init__(self, expr):
        self.expr = expr
        self.pos = 0

    def __getitem__(self, idx):
        return str(self.expr[idx])

    def take(self):
        try:
            ret = self.expr[self.pos]
            self.pos += 1
            return str(ret)
        except:
            raise IndexError("Index out of ", self.expr)

    def print(self):
        print(self.expr[:self.pos], "@", self.expr[self.pos:])

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
    elif re.match("-?[0-9]+", op):
        ret = int(op)
    elif re.match("d[0-9]+", op):
        ret = functor.data[int(op[1:])]
    elif re.match("i[0-9]+", op):
        # expr.print()
        # print(index)
        ret = index[int(op[1:])]
    else:
        expr.print()
        raise NotImplementedError("Invalid token {}".format(op))

    if type(ret) is Functor:
        ret = ret.eval()

    return ret

def build_stmt(ctx, functor, spec, offset, path=tuple(), subs=[], data=[]):
    if functor.dexpr:
        subs = []
        ddepth = 0
        for i in range(len(functor.subs)):
            spath = tuple((*path, i))
            sub, sdepth = build_stmt(ctx, functor.subs[i], spec, offset, spath, functor.subs[i].data)
            for d,iexpr in enumerate(functor.iexpr):
                if path in offset and offset[path][d]:
                    iexpr = ["+"] + iexpr + [offset[path][d]]
                ctx["map"].append((("idx", d, sdepth+1), build_ast(ctx, Expr(iexpr), functor.subs[i].data, sdepth)))
            ddepth = sdepth + 1
            subs.append(sub)
        return build_ast(ctx, Expr(functor.dexpr), functor.data, ddepth), ddepth
    else:
        i = spec[path]
        spath = tuple((*path, i))
        sym, sdepth = build_stmt(ctx, functor.subs[i], spec, offset, spath, functor.subs[i].data)
        if functor.iexpr:
            for d,iexpr in enumerate(functor.iexpr):
                if path in offset and offset[path][d]:
                    iexpr = ["+"] + iexpr + [offset[path][d]]
                ctx["map"].append((("idx", d, sdepth+1), build_ast(ctx, Expr(iexpr), functor.subs[i].data, sdepth)))
        return sym, sdepth+1

def build_ast(ctx, expr, data, depth):
    op = expr.take()
    if op == "+":
        add_a = build_ast(ctx, expr, data, depth)
        add_b = build_ast(ctx, expr, data, depth)
        return ("+", add_a, add_b)
    elif op == "-":
        sub_a = build_ast(ctx, expr, data, depth)
        sub_b = build_ast(ctx, expr, data, depth)
        return ("-", sub_a, sub_b)
    elif op == "*":
        mul_a = build_ast(ctx, expr, data, depth)
        mul_b = build_ast(ctx, expr, data, depth)
        return ("*", mul_a, mul_b)
    elif op == "//":
        idiv_a = build_ast(ctx, expr, data, depth)
        idiv_b = build_ast(ctx, expr, data, depth)
        return ("//", idiv_a, idiv_b)
    elif op == "ref":
        ref_a = build_ast(ctx, expr, data, depth)
        ref_b = build_ast(ctx, expr, data, depth)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        return ("ref", ref_a, ref_b)
    elif op == "d":
        name = data.get_name()
        ctx["data"][name] = ("float", data)
        return name
    elif re.match("-?[0-9]+", op):
        return ("term",op)
    elif re.match("d[0-9]+", op):
        i = int(op[1:])
        return ("term", data[i])
    elif re.match("i[0-9]+", op):
        return ("idx", int(op[1:]), depth)
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
            b = axis_slices[0]
            for e in axis_slices[1:]:
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
        return [x[-1]-x[0] for x in self.shape][idx]

    def size(self):
        size = 1
        for s in self:
            size *= s
        return size

    def ensure_list(self, shape):
        if type(shape) is Shape:
            return shape.shape
        ret = []
        for s in shape:
            if type(s) is int:
                ret.append([0,s])
            else:
                ret.append(list(s))
        return ret

class Data(list):
    acc = 0
    def __init__(self, a, name=None):
        super().__init__(a)
        self.id = Data.acc
        Data.acc += 1
        self.name = name

    def get_name(self):
        if self.name:
            return "d_{}_{}".format(self.name, self.id)
        else:
            return "d_{}".format(self.id)

class Functor():
    acc = 0
    def __init__(self, shape, dtype=None, dexpr=None, iexpr=None, data=None, subs=[], desc=None):
        # external perspective
        self.id = Functor.acc
        Functor.acc += 1
        self.shape = Shape(shape)
        self.dtype = dtype
        self.desc = desc

        # internal perspective
        self.dexpr = dexpr # data expression, evaluate from index/data to value
        self.iexpr = iexpr # index expression, evaluate from sub-functor index to index for this functor
        if data: # static data
            if type(data) is Data:
                self.data = data
            else:
                self.data = Data(data)
        else:
            self.data = None
        self.subs = subs # sub functors

        # runtime
        self.name = None
        self.generated = False
        self.eval_cached = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        d = []
        d.append("id={}".format(self.id ))
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
        print("Functor{}: #{}".format(suffix, self.id))

        print(" "*(indent+1)*indent__num, end="")
        print("{}".format(self.desc))

        print(" "*(indent+1)*indent__num, end="")
        print("shape={}".format(self.shape))

        print(" "*(indent+1)*indent__num, end="")
        print("dexpr={}".format(self.dexpr))

        print(" "*(indent+1)*indent__num, end="")
        print("iexpr={}".format(self.iexpr))

        if self.data:
            print(" "*(indent+1)*indent__num, end="")
            print("data={}".format(self.data))

        for i,s in enumerate(self.subs or []):
            s.print(indent+1, suffix="[{}]".format(i))


    def output(self, dtype, name):
        self.dtype = dtype
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
            data = numpy.zeros(self.shape)
            if self.dexpr:
                slice = self.shape.slices()[0]
                offset = [x[0] for x in slice]
                for idx in itertools.product(*[range(b,b+n) for b,n in slice]):
                    pidx = self.eval_index(idx)
                    data[pidx] = eval_expr(self, Expr(self.dexpr), idx)
            else:
                for i,slice in enumerate(self.shape.slices()):
                    functor = self.subs[i]
                    offset = [x[0] for x in slice]
                    for idx in itertools.product(*[range(n) for n in functor.shape]):
                        pidx = tuple([sum(x) for x in zip(offset, self.eval_index(idx))])
                        v = functor.eval()
                        try:
                            data[pidx] = v[idx]
                        except:
                            print("===== DEBUG ======")
                            print("Sub-Functor", functor)
                            print("iexpr", self.iexpr)
                            print("idx",idx,"offset",offset)
                            print("pidx",pidx)
                            print("data", data.shape)
                            print("==================")
                            raise
            self.eval_cached = data
        return self.eval_cached

    def build_cfg(self, ctx):
        if ctx is None:
            ctx = new_ctx()
        ctx["symbols"][self.name] = (self.dtype, self.shape)

        for slice, spec, offset in self.build_blocks():
            ctx["stmt"].append(("for", [x[1] for x in slice]))
            stmt = []
            mapping = []
            symbol, depth = build_stmt({"symbols":ctx["symbols"], "data":ctx["data"], "stmt": stmt, "map":mapping}, self, spec, offset)
            for m in mapping:
                ctx["stmt"].append(("def", m[0], m[1]))
            ctx["stmt"].append(("=", self, symbol, depth))
            for m in mapping[::-1]:
                ctx["stmt"].append(("undef", m[0]))
            ctx["stmt"].append(("endfor",))

        return ctx

    def build_blocks(self, path=tuple()):
        blocks = []

        if self.dexpr:
            slice = self.shape.slices()[0]
            offset = [x[0] for x in slice]
            for e in Expr(self.dexpr):
                if re.match(r"f[0-9]+", e):
                    i = int(e[1:])
                    sf = self.subs[i]
                    spath = tuple((*path, i))
                    for sub_slice, sub_spec, sub_offset in sf.build_blocks(spath):
                        soffset = dict(sub_offset)
                        soffset[path] = offset
                        blocks.append((sub_slice, sub_spec, soffset))
        else:
            for i,slice in enumerate(self.shape.slices()):
                functor = self.subs[i]
                spath = tuple((*path, i))
                offset = [x[0] for x in slice]

                for sub_slice, sub_spec, sub_offset in self.subs[i].build_blocks(spath):
                    sspec = dict(sub_spec)
                    sspec[path] = i
                    soffset = dict(sub_offset)
                    soffset[path] = offset
                    blocks.append((sub_slice, sspec, soffset))

        if not blocks:
            slice = self.shape.slices()[0]
            blocks.append((slice,{},{}))

        return blocks
