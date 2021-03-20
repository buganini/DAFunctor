import os
from .gen_c import *
from .typing import *
from .pytyping import *
from .expression import *
from .transpiler import *
from .common import *

class Data(list):
    auto_id = 0
    def __init__(self, a, name=None):
        super().__init__(a)
        self.id = Data.auto_id
        Data.auto_id += 1
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
    auto_id = 0
    def __init__(self,
            shape,
            partitions = None,
            dtype = None,
            vexpr = None,
            iexpr = None,
            sexpr = None,
            data = None,
            subs = [],
            desc = None,
            opdesc = None,
            name = None,
            buffer = None,
            src_func = None,
            is_contiguous = False,
        ):
        # external perspective
        self.id = Functor.auto_id
        Functor.auto_id += 1
        self.shape = Shape(shape)
        self.partitions = partitions
        self.dtype = dtype
        self.desc = desc
        self.opdesc = opdesc
        self.name = name
        self.auto_name = None
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

        # internal
        self._daf_src_func = src_func
        self._daf_is_contiguous = is_contiguous

        self._daf_requested_contiguous = False
        self._daf_eval_cached = None
        self._daf_exported = False
        self._daf_is_output = False
        self._daf_is_declared = False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        d = []
        d.append("id={}".format(self.id ))
        d.append("name={}".format(self.get_name() or ""))
        d.append("desc={}".format(self.desc))
        d.append("shape={}".format(self.shape))
        if self.partitions:
            d.append("partitions={}".format(self.partitions))
        if self.iexpr:
            d.append("iexpr={}".format(self.iexpr))
        if self.subs:
            d.append("subs={}".format(len(self.subs)))
        return "Functor({})".format(", ".join(d))

    def __assign__(self, name, idx):
        if not idx is None:
            name = f"{name}_{idx}"
        self.auto_name = name

    def print(self, indent=0, suffix=""):
        indent__num = 4
        print(" "*indent*indent__num, end="")
        print("Functor{}: #{} {}".format(suffix, self.id, self.get_name() or ""))

        print(" "*(indent+1)*indent__num, end="")
        print("{}".format(self.desc))

        print(" "*(indent+1)*indent__num, end="")
        print("shape={}".format(self.shape))

        if not self.dtype is None:
            print(" "*(indent+1)*indent__num, end="")
            print("dtype={}".format(self.dtype))

        if not self.partitions is None:
            print(" "*(indent+1)*indent__num, end="")
            print("partitions={}".format(self.partitions))

        if not self.vexpr is None:
            print(" "*(indent+1)*indent__num, end="")
            print("vexpr={}".format(self.vexpr))

        if not self.sexpr is None:
            print(" "*(indent+1)*indent__num, end="")
            print("sexpr={}".format(self.sexpr))

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

        if self._daf_is_contiguous:
            print(" "*(indent+1)*indent__num, end="")
            print("contiguous")

        if self.daf_is_joiner():
            print(" "*(indent+1)*indent__num, end="")
            print("joiner")

        for i,s in enumerate(self.subs or []):
            s.print(indent+1, suffix="[{}]".format(i))

    def daf_is_contiguous(self):
        return self._daf_is_contiguous or self._daf_requested_contiguous

    def daf_is_joiner(self):
        return len(self.subs) > 1 and not self.partitions

    def eval_index(self, index, sidx=None):
        fidx = None
        if self.iexpr is None:
            fidx = index
        else:
            fidx = tuple([
                eval_expr(self, Expr(iexpr, self, i), index, sidx)
                for i,iexpr in enumerate(self.iexpr)
            ])
        if fidx is None:
            return None
        fidx = [(f-s[0]) for f,s in zip(fidx,self.shape.shape)]
        if not all([(f >= 0) for f,s in zip(fidx,self.shape.shape)]):
            return None
        if not all([(f % s[2])==0 for f,s in zip(fidx,self.shape.shape)]):
            return None
        fidx = [(f//s[2]) for f,s in zip(fidx,self.shape.shape)]
        if not all([(f < s[1]) for f,s in zip(fidx,self.shape.shape)]):
            return None
        return tuple(fidx)

    def eval_scatter(self, data, idx, scatter, value):
        import numpy
        axis,start,num,step = scatter
        for i in range(num):
            sidx = list(idx)
            sidx[axis] += start + i*step
            try:
                data[tuple(sidx)] = value
            except:
                print(f"#{self.id} {scatter}")
                raise

    def eval(self):
        if self._daf_eval_cached is None:
            import numpy
            data = numpy.zeros(self.shape).astype(to_numpy_type(self.get_type()))
            if self.partitions:
                for sidx, rg in enumerate(self.partitions):
                    functor = self.subs[sidx]
                    if rg: # sub-element is a functor
                        for idx in ranger(rg):
                            pidx = self.eval_index(idx, sidx)
                            if pidx is None:
                                continue
                            v = functor.eval()
                            if self.sexpr is None:
                                try:
                                    data[pidx] = v[idx]
                                except:
                                    print("===== DEBUG ======")
                                    print("Sub-Functor", functor)
                                    if self.iexpr:
                                        print("iexpr")
                                        for e in self.iexpr:
                                            print(" ", e)
                                    print("sidx",sidx)
                                    print("idx",idx)
                                    print("v.shape", v.shape)
                                    print("pidx",pidx)
                                    print("data.shape", data.shape)
                                    print("==================")
                                    raise
                            else:
                                self.eval_scatter(data, pidx, self.sexpr, v[idx])
                    else: # sub-element is a scalar value
                        pidx = self.eval_index(None, sidx)
                        if not pidx is None:
                            v = functor.eval()
                            if self.sexpr is None:
                                try:
                                    data[pidx] = v
                                except:
                                        print("===== DEBUG ======")
                                        print("Sub-Functor", functor)
                                        if self.iexpr:
                                            print("iexpr")
                                            for e in self.iexpr:
                                                print(" ", e)
                                        print("sidx",sidx)
                                        print("idx",idx)
                                        print("v", v)
                                        print("pidx",pidx)
                                        print("data.shape", data.shape)
                                        print("==================")
                                        raise
                            else:
                                self.eval_scatter(data, pidx, self.sexpr, v)
            else:
                rg = [(0,s,1) for s in self.shape]
                for idx in ranger(rg):
                    pidx = self.eval_index(idx)
                    if pidx is None:
                        continue
                    v = eval_expr(self, Expr(self.vexpr, self), idx)
                    if self.sexpr is None:
                        data[pidx] = v
                    else:
                        self.eval_scatter(data, pidx, self.sexpr, v)
            self._daf_eval_cached = data
        return self._daf_eval_cached

    def build_cfg(self, ctx=None):
        if ctx is None:
            ctx = CFG()

        transpile(ctx, [self])

        return ctx

    def get_name(self, assign=False):
        name = self.name
        if name is None:
            name = self.auto_name
        if name is None:
            name = f"array{self.id}"
        if assign:
            self.name = name
        return name

    def get_type(self):
        if not self.dtype is None:
            return self.dtype

        return "f"

    def jit(self, *args, cflags=["-O3"]):
        import sys
        import subprocess
        import ctypes
        import numpy

        src_name = f"gen_{self.get_name()}"
        func_name = src_name

        jitdir = os.path.realpath("__jit__")
        os.makedirs(jitdir, exist_ok=True)

        ctx = CFG()
        ctx.append(["func", func_name, [self], args, ctx.data])
        self.build_cfg(ctx.enter())

        cfile = os.path.join(jitdir, src_name+".c")
        with open(cfile, "w") as f:
            gen_func(ctx, f)

        so_path = os.path.join(jitdir, f"{src_name}_{self.id}.so")
        try:
            subprocess.check_output(["cc", "-fPIC"] + cflags + ["-shared", "-o", so_path, cfile])
        except:
            print(open(cfile).read())
            raise

        dll = ctypes.CDLL(so_path)
        f = getattr(dll, func_name)

        from .numpy import NumpyFunctor
        from .torch import TorchFunctor
        if isinstance(self, NumpyFunctor):
            def func(*args):
                dargs = []
                for x in args:
                    if is_functor(x):
                        dargs.append(ctypes.cast(x.buffer, ctypes.c_void_p))
                    elif is_numpy(x):
                        dargs.append(x.ctypes.data_as(ctypes.c_void_p))
                    elif type(x) in (int, float):
                        dargs.append(x)
                    else:
                        raise ValueError(f"Unknown data type {type(x)}")
                ret = numpy.empty(self.shape, dtype=to_numpy_type(self.get_type()))
                pointer = ret.ctypes.data_as(ctypes.c_void_p)
                f(pointer, *dargs)
                return ret
        elif isinstance(self, TorchFunctor):
            def func(*args):
                import torch
                dargs = []
                for x in args:
                    if is_functor(x):
                        dargs.append(ctypes.cast(x.buffer, ctypes.c_void_p))
                    elif is_numpy(x):
                        dargs.append(x.ctypes.data_as(ctypes.c_void_p))
                    elif type(x) in (int, float):
                        dargs.append(x)
                    else:
                        raise ValueError(f"Unknown data type {type(x)}")
                ret = numpy.empty(self.shape, dtype=to_numpy_type(self.get_type()))
                pointer = ret.ctypes.data_as(ctypes.c_void_p)
                f(pointer, *dargs)
                return torch.from_numpy(ret)
        func.source = cfile
        return func

class Buffer(Functor):
    def __init__(self, name, dtype, data):
        import struct
        l = len(data)
        esz = struct.Struct(to_struct_type(dtype)).size
        if l % esz != 0:
            raise ValueError(f"Buffer size {l} must be multiple of data size {esz}")
        super().__init__(
            shape=[l//esz],
            dtype = dtype,
            vexpr = ["buf", ["i0"]],
            buffer = data,
            name = name,
            desc = f"buffer_{name}",
            is_contiguous = True
        )
