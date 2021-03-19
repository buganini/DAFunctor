from . import assign
import inspect

class jit():
    def __init__(self, enable=False):
        self.enable = enable

    def __call__(self, func):
        if self.enable:
            patched_func = assign.patch_func(func, inspect.stack()[1].frame.f_globals)
            def f(*args, **kwargs):
                return patched_func(*args, **kwargs)
            return f
        else:
            return func
