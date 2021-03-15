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
#  v{n} value of n-th sub-functor at specified index
#  d data value
#  si index of sub-functors

from functools import reduce
import re
from .pytyping import *
from .typing import *

class Expr():
    def __init__(self, expr, ref_functor=None, ref_i=None):
        if type(expr) in (int, float, str, Expr) or is_functor(expr):
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
    if is_functor(expr):
        a = expr.eval()
        return a[index]

    if not type(expr) is Expr:
        return expr

    op = expr.op
    if is_number(op):
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
    elif op == ">":
        gt_a = eval_expr(functor, expr[0], index, sidx)
        gt_b = eval_expr(functor, expr[1], index, sidx)
        ret = gt_a > gt_b
    elif op == "?:":
        ie_cond = eval_expr(functor, expr[0], index, sidx)
        ie_if = eval_expr(functor, expr[1], index, sidx)
        ie_else = eval_expr(functor, expr[2], index, sidx)
        ret = ie_if if ie_cond else ie_else
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
        return functor.subs[int(op[1:])].eval()[index]
    elif re.match("pass", op):
        return functor.subs[0].eval()[index]
    elif op  == "buf":
        import struct
        if functor.buffer is None:
            raise AssertionError(f"Reference unset buffer of {functor}")
        buf_idx = eval_expr(functor, expr[0], index, sidx)
        return struct.unpack(to_struct_type(functor.dtype)*functor.shape[0], functor.buffer)[buf_idx]
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if is_functor(ret):
        ret = ret.eval()

    return ret