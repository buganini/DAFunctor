## Operators:
#  * addidion
#  - substraction
#  * multiplication
#  / division
#  // integer division
#  % modulo
#  ref reference

## Value
#  i{n} index on n-th axis
#  d data value

import os
import re
from functools import reduce
from .gen_c import *
from .typing import *
from collections import OrderedDict

class CFG():
    def __init__(self, target, parent=None, data=None):
        self.target = target
        self.parent = parent
        if parent is None:
            self.depth = -1
        else:
            self.depth = parent.depth + 1
        self.data = data
        if self.data is None:
            self.data = OrderedDict()
        self.stmt = []
        self.output = False

    def __repr__(self):
        return str(self.stmt)

    def __str__(self):
        return self.__repr__()

    def append(self, stmt):
        self.stmt.append(stmt)

    def enter(self):
        scope = CFG(self.target, parent=self, data=self.data)
        self.append(["scope", scope])
        return scope

class Expr():
    def __init__(self, expr, ref_functor=None, ref_i=None):
        if type(expr) in (int, float, str, Expr):
            self.op = expr
            self.args = []
        else:
            self.op = expr[0]
            self.args = expr[1]
        self.functor = ref_functor
        self.i = ref_i

    def __getitem__(self, idx):
        return Expr(self.args[idx], self.functor, self.i)

    def __str__(self):
        return f"[{self.op}, [{self.args}]]"

    def __repr__(self):
        return self.__str__()

    def search(self, p):
        todo = [self]
        ret = set()
        while todo:
            t = todo.pop(0)
            if type(t) is Expr:
                todo.append(t.op)
                todo.extend(t.args)
                continue
            if type(t) is str:
                if re.match(p, t):
                    ret.add(t)
        return ret

def eval_expr(functor, expr, index=None):
    if isinstance(expr, Functor):
        return expr.eval()

    if not type(expr) is Expr:
        return expr

    op = expr.op
    if type(op) in (int, float):
        ret = op
    elif op == "+":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x+y, a)
    elif op == "-":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x-y, a)
    elif op == "*":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x*y, a)
    elif op == "//":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x//y, a)
    elif op == "/":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x/y, a)
    elif op == "%":
        a = [eval_expr(functor, e, index) for e in expr]
        ret = reduce(lambda x,y:x%y, a)
    elif op == "ref":
        ref_a = eval_expr(functor, expr[0], index)
        ref_b = eval_expr(functor, expr[1], index)
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
        # print("functor", functor)
        # print("op", op)
        # print("index", index)
        ret = index[int(op[1:])]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if isinstance(ret, Functor):
        ret = ret.eval()

    return ret

def build_cfg(ctx, path):
    value = None
    scope = ctx
    idepth = 0
    for depth, (functor, rg, sidx) in enumerate(path):
        if depth == 0:
            scope.append(["for_shape", [x[1] for x in rg], scope.depth + 1, idepth])
            scope = scope.enter()

        if not functor.dexpr is None:
            if functor.iexpr:
                for d,iexpr in enumerate(functor.iexpr):
                    iexpr = ["+", [iexpr + [rg[d][0]]]]
                    scope.append(["val", "i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), functor.subs[sidx].data, idepth)])
                idepth += 1
            value = build_ast(scope, Expr(functor.dexpr), functor.data, depth)
        else:
            if functor.iexpr:
                for d,iexpr in enumerate(functor.iexpr):
                    iexpr = ["+", [iexpr,  rg[d][0]]]
                    scope.append(["val","i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), functor.subs[sidx].data, idepth)])
                idepth += 1

        output = False

        final_out = depth + 1 == len(path)
        if not functor.sexpr is None: # scatter
            val = ["v", scope.depth]
            scope.append(["val", path[-1][0].get_type(), val, value])
            scope.append(["for_scatter", functor.shape, functor.sexpr, scope.depth + 1, idepth])
            scope = scope.enter()
            value = val
        if final_out:
            scope.append(["=", functor, value, idepth, scope.depth])

def build_ast(ctx, expr, data, depth):
    op = expr.op
    if type(op) in (int, float):
        return op
    elif op in ("+","-","*","//","/","%"):
        args = [build_ast(ctx, e, data, depth) for e in expr]
        return [op, args]
    elif op == "ref":
        ref_a = build_ast(ctx, expr[0], data, depth)
        ref_b = build_ast(ctx, expr[1], data, depth)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        return ["ref", ref_a, ref_b]
    elif op == "d":
        name = data.get_name()
        ctx.data[name] = (data.get_type(), data)
        return name
    elif re.match("-?[0-9]+", op):
        return ["term",op]
    elif re.match("d[0-9]+", op):
        i = int(op[1:])
        return ["term", data[i]]
    elif re.match("i[0-9]+", op):
        return ["idx", int(op[1:]), ctx.depth, depth]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

class Data(list):
    acc = 0
    def __init__(self, a, name=None):
        super().__init__(a)
        self.id = Data.acc
        Data.acc += 1
        self.name = name
        self.dtype = get_list_type(a)

    def get_name(self):
        if self.name:
            return "d_{}_{}".format(self.name, self.id)
        else:
            return "d_{}".format(self.id)

    def get_type(self):
        return self.dtype

class Functor():
    acc = 0
    def __init__(self, shape, ranges=None, dtype=None, dexpr=None, iexpr=None, sexpr=None, data=None, subs=[], desc=None):
        # external perspective
        self.id = Functor.acc
        Functor.acc += 1
        self.shape = tuple(shape)
        self.ranges = ranges
        self.dtype = dtype
        self.desc = desc

        # internal perspective
        self.dexpr = dexpr # data expression, evaluate from index/data to value
        self.iexpr = iexpr # index expression, evaluate from sub-functor index to index for this functor
        self.sexpr = sexpr # scatter expression, map one index to multiple indices
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
        if self.ranges:
            d.append("ranges={}".format(self.ranges))
        if self.iexpr:
            d.append("iexpr={}".format(self.iexpr))
        if self.subs:
            d.append("subs={}".format(len(self.subs)))
        return "Functor({})".format(", ".join(d))

    def print(self, indent=0, suffix=""):
        indent__num = 4
        print(" "*indent*indent__num, end="")
        print("Functor{}: #{}".format(suffix, self.id))

        print(" "*(indent+1)*indent__num, end="")
        print("{}".format(self.desc))

        print(" "*(indent+1)*indent__num, end="")
        print("shape={}".format(self.shape))

        if not self.ranges is None:
            print(" "*(indent+1)*indent__num, end="")
            print("ranges={}".format(self.ranges))

        if not self.dexpr is None:
            print(" "*(indent+1)*indent__num, end="")
            print("dexpr={}".format(self.dexpr))

        if self.iexpr:
            print(" "*(indent+1)*indent__num, end="")
            print("iexpr=[".format(self.iexpr))

            for e in self.iexpr:
                print(" "*(indent+1+2)*indent__num, end="")
                print(e)

            print(" "*(indent+1)*indent__num, end="")
            print("]".format(self.iexpr))

        if self.data:
            print(" "*(indent+1)*indent__num, end="")
            print("data={}".format(self.data))

        for i,s in enumerate(self.subs or []):
            s.print(indent+1, suffix="[{}]".format(i))

    def get_ranges(self):
        if self.ranges is None:
            return [[
                (0,s,1)
                for s in self.shape
            ]]
        else:
            return self.ranges

    def eval_index(self, index):
        if self.iexpr is None:
            return index
        else:
            return tuple([
                eval_expr(self, Expr(iexpr, self, i), index)
                for i,iexpr in enumerate(self.iexpr)
            ])

    def eval_scatter(self, data, idx, scatters):
        if scatters is None:
            return
        for axis,start,num,step in scatters:
            for i in range(num):
                sidx = list(idx)
                sidx[axis] += start + i*step
                data[tuple(sidx)] = data[idx]

    def eval(self):
        if self.eval_cached is None:
            import itertools
            import numpy
            data = numpy.zeros(self.shape)
            if not self.dexpr is None:
                rg = self.get_ranges()[0]
                offset = [x[0] for x in rg]
                for idx in itertools.product(*[range(base,base+num*step,step) for base,num,step in rg]):
                    pidx = self.eval_index(idx)
                    data[pidx] = eval_expr(self, Expr(self.dexpr, self), idx)
                    self.eval_scatter(data, pidx, self.sexpr)
            else:
                for i, rg in enumerate(self.get_ranges()):
                    functor = self.subs[i]
                    offset = [x[0] for x in rg]
                    for idx in itertools.product(*[range(n) for n in functor.shape]):
                        pidx = tuple([sum(x) for x in zip(offset, self.eval_index(idx))])
                        v = functor.eval()
                        try:
                            data[pidx] = v[idx]
                        except:
                            print("===== DEBUG ======")
                            print("Sub-Functor", functor)
                            print("iexpr")
                            for e in self.iexpr:
                                print(" ", e)
                            print("idx",idx,"offset",offset)
                            print("pidx",pidx)
                            print("data", data.shape)
                            print("==================")
                            raise
                        self.eval_scatter(data, pidx, self.sexpr)
            self.eval_cached = data
        return self.eval_cached

    def build_cfg(self, ctx=None):
        if ctx is None:
            ctx = CFG(self)

        for path in self.build_blocks():
            build_cfg(ctx, path)
        return ctx

    def build_blocks(self):
        paths = []
        if not self.dexpr is None:
            rg = self.get_ranges()[0]
            for i in range(len(self.subs)):
                for b in self.subs[i].build_blocks():
                    paths.append(b + [(self, rg, i)])
        else:
            for i,rg in enumerate(self.get_ranges()):
                for b in self.subs[i].build_blocks():
                    paths.append(b + [(self, rg, i)])

        if not paths:
            rg = self.get_ranges()[0]
            paths.append([(self, rg, 0)])

        return paths

    def get_name(self):
        if self.name is None:
            self.name = f"tensor{self.id}"
        return self.name

    def get_type(self):
        if not self.dtype is None:
            return self.dtype

        return "f"

    def jit(self, *args, cflags=["-O2"]):
        import sys
        import subprocess
        import ctypes
        import numpy

        fname = f"gen_{self.get_name()}"

        jitdir = os.path.realpath("__jit__")
        os.makedirs(jitdir, exist_ok=True)

        ctx = CFG(self)
        ctx.append(["func", self, args])
        self.build_cfg(ctx)
        ctx.append(["endfunc"])

        cfile = os.path.join(jitdir, fname+".c")
        with open(cfile, "w") as f:
            gen_func(ctx, f)

        so_path = os.path.join(jitdir, f"{fname}_{self.id}.so")
        try:
            subprocess.check_output(["cc", "-fPIC"] + cflags + ["-shared", "-o", so_path, cfile])
        except:
            print(open(cfile).read())
            raise

        dll = ctypes.CDLL(so_path)
        f = getattr(dll, fname)
        def func(*args):
            args = [x.ctypes.data_as(ctypes.c_void_p) for x in args]
            ret = numpy.zeros(self.shape, dtype=to_numpy_type(self.get_type()))
            pointer = ret.ctypes.data_as(ctypes.c_void_p)
            f(pointer, *args)
            return ret
        func.source = cfile
        return func