import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import ndafunctor.numpy as nf
import pprint

pp = pprint.PrettyPrinter()

def test_func(test, f, *args, params=tuple(), **kwargs):
    try:
        golden = f(np, *args, **kwargs)
    except:
        print(f"\x1b[1;31mgolden eval failed\x1b[m: {test}")
        raise

    try:
        symbols = f(nf, *args, **kwargs)
        symbols.name = test
    except:
        print(f"\x1b[1;31mconstruct failed\x1b[m: {test}")
        raise

    try:
        ev = symbols.eval()
    except:
        symbols.print()
        print(f"\x1b[1;31meval failed\x1b[m: {test}")
        raise
    if not np.array_equal(golden, ev):
        print("Golden", golden)
        print("Eval", ev)
        symbols.print()
        print(f"\x1b[1;31meval() mismatch\x1b[m: {test}")
        raise ValueError(f"eval() mismatch: {test}")

    try:
        func = symbols.jit(*params)
    except:
        symbols.print()
        try:
            pp.pprint(symbols.build_cfg())
        except:
            print("Unable to build CFG")
        print(f"\x1b[1;31mjit failed\x1b[m: {test}")
        raise

    try:
        cv = func(*args)
    except:
        print(f"\x1b[1;31mjit function invocation failed\x1b[m: {test}")

    if not np.array_equal(golden, cv):
        symbols.print()
        try:
            pp.pprint(symbols.build_cfg())
        except:
            print("Unable to build CFG")
        print(open(func.source).read())
        print("Golden", golden)
        print("JitEval", cv)
        print(f"\x1b[1;31mjit() mismatch\x1b[m: {test}")
        raise ValueError(f"jit() mismatch: {test}")

    print("\x1b[1;32mOK\x1b[m", test)

    import timeit
    iter = 1000
    numpy_time = timeit.timeit(lambda: f(np, *args, **kwargs), number=iter)
    ndaf_time = timeit.timeit(lambda: func(*args), number=iter)
    print("  Gain", numpy_time/ndaf_time)

if __name__=="__main__":
    import importlib
    for fn in sorted(os.listdir(os.path.dirname(os.path.abspath(__file__)))):
        if fn.startswith("numpy_"):
            try:
                importlib.import_module(os.path.splitext(fn)[0])
            except:
                pass
