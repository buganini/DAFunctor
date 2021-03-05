import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import ndafunctor.numpy as nf
import pprint

pp = pprint.PrettyPrinter()

def test_func(test, f, *args, params=tuple(), **kwargs):
    golden = f(np, *args, **kwargs)

    symbols = f(nf, *args, **kwargs)
    symbols.name = test

    try:
        ev = symbols.eval()
    except:
        symbols.print()
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
        pp.pprint(symbols.build_cfg())
        raise

    cv = func(*params)
    if not np.array_equal(golden, cv):
        symbols.print()
        pp.pprint(symbols.build_cfg())
        print(open(func.source).read())
        print("Golden", golden)
        print("JitEval", cv)
        print(f"\x1b[1;31mjit() mismatch\x1b[m: {test}")
        raise ValueError(f"jit() mismatch: {test}")

    print("\x1b[1;32mOK\x1b[m", test)

if __name__=="__main__":
    import importlib
    for fn in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if fn.startswith("numpy_"):
            try:
                importlib.import_module(os.path.splitext(fn)[0])
            except:
                pass
