## Operators:
#  * addidion
#  - substraction
#  * multiplication
#  / division
#  // integer division
#  ref reference
#  len length
#  transpose transpose

## Value
#  i dimentional index
#  r register value

import re

def eval_expr(tensor, expr, index=None, pos=0):
    if type(expr) is ITensor:
        return expr.eval()
    if not type(expr) is list:
        return expr
    op = expr[pos]
    if op == "+":
        add_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        add_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = add_a + add_b, 1+tks_a+tks_b
    elif op == "-":
        sub_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        sub_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = sub_a - sub_b, 1+tks_a+tks_b
    elif op == "*":
        mul_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        mul_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = mul_a * mul_b, 1+tks_a+tks_b
    elif op == "//":
        idiv_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        idiv_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        ret = idiv_a // idiv_b, 1+tks_a+tks_b
    elif op == "ref":
        ref_a, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        ref_b, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        ret = ref_a[ref_b], 1+tks_a+tks_b
    elif op == "transpose":
        transpose_map, tks_a = eval_expr(tensor, expr, index, pos=pos+1)
        transpose_idx, tks_b = eval_expr(tensor, expr, index, pos=pos+1+tks_a)
        transposed_index = [transpose_idx[transpose_map[i]] for i in range(len(transpose_idx))]
        ret = transposed_index, 1+tks_a+tks_b
    elif op == "i":
        ret = index, 1
    elif op == "r":
        ret = tensor.regs, 1
    elif re.match("-?[0-9]+", op):
        ret = int(op), 1
    elif re.match("r[0-9]+", op):
        ret = tensor.regs[int(op[1:])], 1
    elif re.match("i[0-9]+", op):
        ret = index[int(op[1:])], 1
    else:
        raise NotImplementedError("Invalid token {}".format(op))

    if type(ret[0]) is ITensor:
        ret = ret[0].eval(), ret[1]

    if pos==0:
        return ret[0]
    else:
        return ret

class ITensor():
    def __init__(self, regs, shape, func, offset=None):
        self.regs = regs
        self.shape = shape
        self.func = func
        self.offset = offset

    def __str__(self):
        return "" \
            f"Offset: {self.offset}\n" \
            f"Shape: {self.shape}\n" \
            f"Func: {self.func}\n" \
            f"Regs: {self.regs}\n"

    def eval(self):
        import itertools
        import numpy
        shape = list([eval_expr(self, s) for s in self.shape])
        data = []
        for idx in itertools.product(*[range(s) for s in shape]):
            data.append(eval_expr(self, self.func, idx))
        return numpy.array(data).reshape(shape)
