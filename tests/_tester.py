import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import ndafunctor as nf
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
        raise ValueError("eval() mismatch")

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
        print("Golden", golden)
        print("JitEval", cv)
        raise ValueError("jit() mismatch")

    print("OK", test)