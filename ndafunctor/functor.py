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
#  si index of sub-functors

import os
import re
from functools import reduce
from .gen_c import *
from .typing import *
from collections import OrderedDict

def ranger(rg):
    import itertools
    return itertools.product(*[range(base,base+num*step,step) for base,num,step in rg])

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

def eval_expr(functor, expr, index=None, sidx=None):
    if isinstance(expr, Functor):
        return expr.eval()

    if not type(expr) is Expr:
        return expr

    op = expr.op
    if type(op) in (int, float):
        ret = op
    elif op == "+":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x+y, a)
    elif op == "-":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x-y, a)
    elif op == "*":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x*y, a)
    elif op == "//":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x//y, a)
    elif op == "/":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x/y, a)
    elif op == "%":
        a = [eval_expr(functor, e, index, sidx) for e in expr]
        ret = reduce(lambda x,y:x%y, a)
    elif op == "ref":
        ref_a = eval_expr(functor, expr[0], index, sidx)
        ref_b = eval_expr(functor, expr[1], index, sidx)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        # print("ref_a", ref_a)
        # print("ref_b", ref_b)
        ret = ref_a[ref_b]
    elif op == "si":
        return sidx
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
        idx = int(op[1:])
        try:
            ret = index[idx]
        except:
            print(f"#{functor.id} {op}: {index}[{idx}]")
            raise
    elif re.match("v[0-9]+", op):
        return functor.subs[int(op[1:])][index]
    elif op  == "buf":
        import struct
        if functor.buffer is None:
            raise AssertionError(f"Reference unset buffer of {functor}")
        buf_idx = eval_expr(functor, expr[0], index, sidx)
        return struct.unpack(to_struct_type(functor.dtype)*functor.shape[0], functor.buffer)[buf_idx]
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
            scope.append(["for_shape", rg, scope.depth + 1, idepth])
            scope = scope.enter()

        if functor.partitions:
            if functor.iexpr:
                for d,iexpr in enumerate(functor.iexpr):
                    scope.append(["val","i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), sidx, functor.subs[sidx], idepth)])
                idepth += 1
        else:
            if functor.iexpr:
                for d,iexpr in enumerate(functor.iexpr):
                    scope.append(["val", "i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), sidx, functor.subs[sidx], idepth)])
                idepth += 1
            value = build_ast(scope, Expr(functor.vexpr), sidx, functor, depth)

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

def build_ast(ctx, expr, sidx, functor, depth):
    op = expr.op
    if type(op) in (int, float):
        return op
    elif op in ("+","-","*","//","/","%"):
        args = [build_ast(ctx, e, sidx, functor, depth) for e in expr]
        return [op, args]
    elif op == "ref":
        ref_a = build_ast(ctx, expr[0], sidx, functor, depth)
        ref_b = build_ast(ctx, expr[1], sidx, functor, depth)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        return ["ref", ref_a, ref_b]
    elif op == "si":
        return sidx
    elif op == "d":
        name = functor.data.get_name()
        ctx.data[name] = (functor.data.get_type(), functor.data)
        return name
    elif re.match("-?[0-9]+", op):
        return ["term",op]
    elif re.match("d[0-9]+", op):
        i = int(op[1:])
        return ["term", functor.data[i]]
    elif re.match("i[0-9]+", op):
        return ["idx", int(op[1:]), ctx.depth, depth]
    elif op == "buf":
        buf_idx = build_ast(ctx, expr[0], sidx, functor, depth)
        return ["ref", functor.name, buf_idx]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

def tailor_shape(paths):
    ret = []
    for path in paths:
        bfunctor, brg, bsidx = path[0]
        vs = [set() for i in range(len(bfunctor.shape))]

        for idx in ranger(brg):
            cidx = idx
            in_range = True

            if bfunctor.partitions:
                raise ValueError(f"Partitioned root functor {bfunctor}")
            else:
                pidx = bfunctor.eval_index(idx)

            if pidx is None:
                continue

            idx = pidx

            for functor, rg, sidx in path[1:]:
                if functor.partitions:
                    sfunctor = functor.subs[sidx]
                    srg = functor.partitions[sidx]
                    if len(idx) != len(srg):
                        raise AssertionError(f"Dimension mismatch {idx} {srg}")
                    if not all([i>=r[0] for i,r in zip(idx, srg)]):
                        in_range = False
                        break
                    if not all([i<r[0]+r[1]*r[2] for i,r in zip(idx, srg)]):
                        in_range = False
                        break
                    if not all([(i-r[0]) % r[2] == 0 for i,r in zip(idx, srg)]):
                        in_range = False
                        break

                pidx = functor.eval_index(idx, sidx)

                if pidx is None:
                    in_range = False
                    break

                idx = pidx

            if in_range:
                for i,c in enumerate(cidx):
                    vs[i].add(c)

        # slices generation
        # TODO: handle step > 1
        num = [len(v) for v in vs]
        if all([n > 0 for n in num]):
            base = [min(v) for v in vs]
            path[0][1] = [(b,n,1) for b,n in zip(base, num)]
            ret.append(path)
    return ret

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

class Shape():
    def __init__(self, shape):
        self.shape = self.ensure_schema(shape)

    def __str__(self):
        return str(self.shape)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.shape)

    def __getitem__(self, idx):
        s = [x[1] for x in self.shape]
        return s.__getitem__(idx)

    def ensure_schema(self, shape):
        if type(shape) is Shape:
            return tuple(shape.shape)

        if all([type(x) is int for x in shape]):
            return tuple([(0,x,1) for x in shape])

        valid = True
        sh = []
        for x in shape:
            if type(x) is int:
                sh.append((0,x,1))
            elif len(x) == 3 and all([type(e) is int for e in x]):
                sh.append(tuple(x))
            else:
                valid = False
                break
        if valid:
            return tuple(sh)

        raise ValueError(f"Invalid shape {shape}")

class Functor():
    acc = 0
    def __init__(self, shape, partitions=None, dtype=None, vexpr=None, iexpr=None, sexpr=None, data=None, subs=[], desc=None, name=None, buffer=None):
        # external perspective
        self.id = Functor.acc
        Functor.acc += 1
        self.shape = Shape(shape)
        self.partitions = partitions
        self.dtype = dtype
        self.desc = desc
        self.name = name
        self.buffer = buffer

        # internal perspective
        self.vexpr = vexpr # value expression, evaluate from index/data to value
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
        self.generated = False
        self.eval_cached = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        d = []
        d.append("id={}".format(self.id ))
        d.append("desc={}".format(self.desc))
        d.append("shape={}".format(self.shape))
        if self.partitions:
            d.append("partitions={}".format(self.partitions))
        if self.iexpr:
            d.append("iexpr={}".format(self.iexpr))
        if self.subs:
            d.append("subs={}".format(len(self.subs)))
        return "Functor({})".format(", ".join(d))

    def print(self, indent=0, suffix=""):
        indent__num = 4
        print(" "*indent*indent__num, end="")
        print("Functor{}: #{} {}".format(suffix, self.id, self.name or ""))

        print(" "*(indent+1)*indent__num, end="")
        print("{}".format(self.desc))

        print(" "*(indent+1)*indent__num, end="")
        print("shape={}".format(self.shape))

        if not self.partitions is None:
            print(" "*(indent+1)*indent__num, end="")
            print("partitions={}".format(self.partitions))

        if not self.vexpr is None:
            print(" "*(indent+1)*indent__num, end="")
            print("vexpr={}".format(self.vexpr))

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

    def eval_index(self, index, sidx=None):
        fidx = None
        if self.iexpr is None:
            fidx = index
        else:
            fidx = tuple([
                eval_expr(self, Expr(iexpr, self, i), index, sidx)
                for i,iexpr in enumerate(self.iexpr)
            ])
        fidx = [(f-s[0]) for f,s in zip(fidx,self.shape.shape)]
        if not all([(f >= 0) for f,s in zip(fidx,self.shape.shape)]):
            return None
        if not all([(f % s[2])==0 for f,s in zip(fidx,self.shape.shape)]):
            return None
        fidx = [(f//s[2]) for f,s in zip(fidx,self.shape.shape)]
        if not all([(f < s[1]) for f,s in zip(fidx,self.shape.shape)]):
            return None
        return tuple(fidx)

    def eval_scatter(self, data, idx, scatter):
        if scatter is None:
            return
        axis,start,num,step = scatter
        for i in range(num):
            sidx = list(idx)
            sidx[axis] += start + i*step
            data[tuple(sidx)] = data[idx]

    def eval(self):
        if self.eval_cached is None:
            import numpy
            data = numpy.zeros(self.shape)
            if self.partitions:
                for sidx, rg in enumerate(self.partitions):
                    functor = self.subs[sidx]
                    for idx in ranger(rg):
                        pidx = self.eval_index(idx, sidx)
                        if pidx is None:
                            continue
                        v = functor.eval()
                        try:
                            data[pidx] = v[idx]
                        except:
                            print("===== DEBUG ======")
                            print("Sub-Functor", functor)
                            print("iexpr")
                            for e in self.iexpr:
                                print(" ", e)
                            print("sidx",sidx)
                            print("idx",idx)
                            print("pidx",pidx)
                            print("data.shape", data.shape)
                            print("==================")
                            raise
                        self.eval_scatter(data, pidx, self.sexpr)
            else:
                rg = [(0,s,1) for s in self.shape]
                for idx in ranger(rg):
                    pidx = self.eval_index(idx)
                    if pidx is None:
                        continue
                    data[pidx] = eval_expr(self, Expr(self.vexpr, self), idx)
                    self.eval_scatter(data, pidx, self.sexpr)
            self.eval_cached = data
        return self.eval_cached

    def build_cfg(self, ctx=None):
        if ctx is None:
            ctx = CFG(self)

        paths = self.build_blocks()
        paths = tailor_shape(paths)
        for path in paths:
            build_cfg(ctx, path)
        return ctx

    def build_blocks(self):
        paths = []
        rg = self.shape.shape

        if self.partitions:
            for i,_ in enumerate(self.partitions):
                for b in self.subs[i].build_blocks():
                    paths.append(b + [[self, rg, i]])
        else:
            for i in range(len(self.subs)):
                for b in self.subs[i].build_blocks():
                    paths.append(b + [[self, rg, i]])

        if not paths:
            paths.append([[self, rg, 0]])

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
            dargs = []
            for x in args:
                if isinstance(x, Functor):
                    dargs.append(ctypes.cast(x.buffer, ctypes.c_void_p))
                elif isinstance(x, numpy.ndarray):
                    dargs.append(x.ctypes.data_as(ctypes.c_void_p))
                elif type(x) in (int, float):
                    dargs.append(x)
                else:
                    raise ValueError(f"Unknown data type {type(x)}")
            ret = numpy.zeros(self.shape, dtype=to_numpy_type(self.get_type()))
            pointer = ret.ctypes.data_as(ctypes.c_void_p)
            f(pointer, *dargs)
            return ret
        func.source = cfile
        return func

class Buffer(Functor):
    def __init__(self, name, dtype, data):
        import struct
        l = len(data)
        esz = struct.Struct(to_struct_type(dtype)).size
        if l % esz != 0:
            raise ValueError(f"Buffer size {l} cannot be devided by data size {esz}")
        super().__init__(
            shape=[l//esz],
            dtype = dtype,
            vexpr = ["buf", ["i0"]],
            buffer = data,
            name = name,
            desc = f"buffer_{name}"
        )
