import numpy as np
import pprint

pp = pprint.PrettyPrinter()

def check_eq(test, golden, symbols, *args):
    symbols.name = test

    try:
        ev = symbols.eval()
    except:
        symbols.print()
        raise
    if not np.array_equal(golden, ev):
        print("Golden", golden)
        print("Eval", ev)
        raise ValueError("eval() mismatch")

    try:
        func = symbols.jit(*args)
    except:
        symbols.print()
        raise

    cv = func(*args)
    if not np.array_equal(golden, cv):
        symbols.print()
        pp.pprint(symbols.build_cfg())
        print("Golden", golden)
        print("JitEval", cv)
        raise ValueError("jit() mismatch")

    print("OK", test)