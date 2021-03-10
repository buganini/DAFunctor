import functools
from .common import *
from .typing import *

intent_spaces = 4

def gen_c_expr(scope, expr, output, indent=0):
    if type(expr) in (str, int, float):
        return str(expr)

    if expr[0] == "for_shape":
        shape = expr[1]
        scope_depth = expr[2]
        idepth = expr[3]
        for i in rangel(shape):
            start, num, step = shape[i]
            end =  start + num * step
            output.write(" "*indent*intent_spaces)
            idx = gen_c_expr(scope, ["idx", i, scope_depth, idepth], output, indent=0)
            output.write("{}for(int {idx}={start};{idx}<{end};{idx}+={step})\n".format(" "*i*2, idx=idx, start=start, end=end, step=step))
        return indent

    elif expr[0] == "for_scatter":
        shape = expr[1]
        scatter = expr[2]
        scope_depth = expr[3]
        idepth = expr[4]
        axis = scatter[0]
        start = scatter[1]
        num = scatter[2]
        step = scatter[3]
        end =  start + num * step
        for d in rangel(shape):
            if d != axis:
                idx = gen_c_expr(scope, ["idx", d, scope_depth, idepth], output, indent=0)
                fidx = gen_c_expr(scope, ["idx", d, scope_depth-1, idepth], output, indent=0)
                output.write(" "*indent*intent_spaces)
                output.write(f"const int {idx} = {fidx};\n")

        offset = gen_c_expr(scope, ["idx", axis, scope_depth-1, idepth], output, indent=0)
        idx = gen_c_expr(scope, ["idx", axis, scope_depth, idepth], output, indent=0)
        output.write(" "*indent*intent_spaces)
        output.write("for(int {idx}={start}+{offset};{idx}<{end}+{offset};{idx}+={step})\n".format(idx=idx, start=start, end=end, step=step, offset=offset))
        return indent

    elif expr[0] == "=":
        tensor = expr[1]
        value_expr = expr[2]
        idepth = expr[3]
        scope_depth = expr[4]
        idx = []
        for i in rangel(tensor.shape):
            didx = [gen_c_expr(scope, ["idx", i, scope_depth, idepth], output, indent=0)]
            for j in range(i+1,len(tensor.shape)):
                didx.append("{}".format(tensor.shape[j]))
            idx.append("*".join(didx))
        idx = " + ".join(idx)
        output.write(" "*(indent)*intent_spaces)
        output.write("{name}[{idx}] = ".format(name=tensor.get_name(), idx=idx))
        output.write(gen_c_expr(scope, value_expr, output, indent=indent+1))
        output.write(";\n")
        return indent

    elif expr[0] == "idx": # axis, scope_depth, iexpr_depth
        sn = list(expr[1:])
        while sn and sn[-1] == 0:
            sn.pop()
        if not sn:
            sn = [0]
        return "i" + "_".join([str(x) for x in sn])

    elif expr[0] == "v":
        return f"v{expr[1]}"

    elif expr[0] == "scope":
        scope = expr[1]
        output.write(" "*indent*intent_spaces)
        output.write("{\n")
        indent += 1
        for expr in scope.stmt:
            indent = gen_c_expr(scope, expr, output, indent)
        indent -= 1
        output.write(" "*indent*intent_spaces)
        output.write("}\n")
        return indent

    elif expr[0] == "autobuf":
        functor = expr[1]
        dtype = to_c_type(functor.get_type())
        name = functor.get_name()
        size = ' * '.join([str(x) for x in functor.shape])
        output.write(" "*indent*intent_spaces)
        output.write(f"AUTOBUF {dtype} {name}[{size}];\n")
        return indent

    elif expr[0] == "val":
        dtype = to_c_type(expr[1])
        name = gen_c_expr(scope, expr[2], output, indent=0)
        expr = gen_c_expr(scope, expr[3], output, indent=0)
        output.write(" "*indent*intent_spaces)
        output.write(f"const {dtype} {name} = {expr};\n")
        return indent

    elif expr[0] == "ref":
        a = gen_c_expr(scope, expr[1], output, indent=0)
        b = gen_c_expr(scope, expr[2], output, indent=0)
        return f"{a}[{b}]"

    elif expr[0] == "+":
        args = [gen_c_expr(scope, e, output, indent=0) for e in expr[1]]
        return "".join(["(", "+".join(args), ")"])

    elif expr[0] == "-":
        args = [gen_c_expr(scope, e, output, indent=0) for e in expr[1]]
        return "".join(["(", "-".join(args), ")"])

    elif expr[0] == "*":
        args = [gen_c_expr(scope, e, output, indent=0) for e in expr[1]]
        return "".join(["(", "*".join(args), ")"])

    elif expr[0] == "//":
        # XXX float args
        args = [gen_c_expr(scope, e, output, indent=0) for e in expr[1]]
        return "".join(["(", "/".join(args), ")"])

    elif expr[0] == "%":
        args = [gen_c_expr(scope, e, output, indent=0) for e in expr[1]]
        return "".join(["(", "%".join(args), ")"])

    elif expr[0] == "term":
        return str(expr[1])

    elif expr[0] == "comment":
        output.write("\n");
        output.write(" "*indent*intent_spaces)
        output.write(f"// {expr[1]}\n\n");
        return indent

    elif expr[0] == "func":
        out = expr[1]
        params = expr[2]
        const_data = expr[3]

        output.write(" "*indent*intent_spaces)
        args = [f"{to_c_type(out.get_type())} * {out.name} /* {list(out.shape)}={functools.reduce(lambda x,y:x*y, out.shape)} */"]
        for p in params:
            args.append(f"{to_c_type(p.get_type())} * {p.name} /* {list(p.shape)}={functools.reduce(lambda x,y:x*y, p.shape)} */")
        output.write("void gen_{}({})\n".format(out.name, ", ".join(args)))

        output.write(" "*indent*intent_spaces)
        output.write("{\n")

        indent += 1

        if const_data:
            for sym_name in const_data:
                dtype, data = const_data[sym_name]
                isarray = True
                output.write(" "*indent*intent_spaces)
                output.write("const static {dtype} {name}".format(dtype=to_c_type(dtype), name=sym_name))
                if isarray:
                    output.write("[] = {")
                    output.write(",".join([str(x) for x in data]))
                    output.write("};\n")
                else:
                    output.write(" = ")
                    output.write(data)
                    output.write(";\n")
            output.write("\n")

        return indent

    elif expr[0] == "endfunc":
        output.write(" "*(indent-1)*intent_spaces)
        output.write("}\n\n")
        return indent - 1

    else:
        raise NotImplementedError("Unknown expr op {}".format(expr[0]))

def gen_func(ctx, output):
    output.write("#include <stdio.h>\n")
    output.write("#include <math.h>\n")
    output.write("#define AUTOBUF\n")
    output.write("\n")

    indent = 0
    for expr in ctx.stmt:
        indent = gen_c_expr(ctx, expr, output, indent)

