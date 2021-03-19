from . import assign
from .typing import *
from .pytyping import *
from .transpiler import CFG, transpile
from .gen_c import gen_func
import inspect

class jit():
    def __init__(self, enable=False, cflags=["-O3"]):
        self.enable = enable
        self.cflags = cflags

    def __call__(self, func):
        if self.enable:
            if func.__code__.co_filename == "__assign__":
                return func

            patched_func = assign.patch_func(func, inspect.stack()[1].frame.f_globals)
            def f(*args, **kwargs):
                import os
                import sys
                import subprocess
                import ctypes
                import numpy

                outs = patched_func(*args, **kwargs)

                single_out = False
                if is_functor(outs):
                    single_out = True
                    outs = [outs]

                fname = func.__name__

                jitdir = os.path.realpath("__jit__")
                os.makedirs(jitdir, exist_ok=True)

                ctx = CFG()
                ctx.append(["func", func.__name__, outs, args, ctx.data])
                transpile(ctx, outs)
                ctx.append(["endfunc"])

                cfile = os.path.join(jitdir, fname+".c")
                with open(cfile, "w") as f:
                    gen_func(ctx, f)

                so_path = os.path.join(jitdir, f"{func.__name__}.so")
                try:
                    subprocess.check_output(["cc", "-fPIC"] + self.cflags + ["-shared", "-o", so_path, cfile])
                except:
                    print(open(cfile).read())
                    raise

                dll = ctypes.CDLL(so_path)
                f = getattr(dll, fname)

                def wfunc(*args):
                    from .numpy import NumpyFunctor
                    from .torch import TorchFunctor
                    import torch
                    iargs = []
                    for x in args:
                        if is_functor(x):
                            iargs.append(ctypes.cast(x.buffer, ctypes.c_void_p))
                        elif is_numpy(x):
                            iargs.append(x.ctypes.data_as(ctypes.c_void_p))
                        elif type(x) in (int, float):
                            iargs.append(x)
                        else:
                            raise ValueError(f"Unknown data type {type(x)}")

                    ret = []
                    oargs = []
                    for x in outs:
                        o = numpy.empty(x.shape, dtype=to_numpy_type(x.get_type()))
                        ret.append(o)
                        oargs.append(o.ctypes.data_as(ctypes.c_void_p))

                    f(*oargs, *iargs)

                    for i,x in enumerate(outs):
                        if isinstance(x, TorchFunctor):
                            ret[i] = torch.from_numpy(ret[i])

                    if single_out:
                        return ret[0]
                    else:
                        return ret
                wfunc.source = cfile
                return wfunc
            return f
        else:
            def f(*args, **kwargs):
                return func
            return f
