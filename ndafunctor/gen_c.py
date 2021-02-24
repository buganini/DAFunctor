import functools

intent_spaces = 4

def gen_c_expr(expr, output, indent=0):
    if type(expr) in (str, int, float):
        return str(expr)

    if expr[0] == "for":
        shape = expr[1]
        for i in range(len(shape)):
            output.write(" "*indent*intent_spaces)
            output.write("{}for(int i{i}=0;i{i}<{n};i{i}++)\n".format(" "*i*2, i=i, n=shape[i]))
        output.write(" "*indent*intent_spaces)
        output.write("{\n")
        return indent + 1

    elif expr[0] == "endfor":
        output.write(" "*(indent-1)*intent_spaces)
        output.write("}\n")
        return indent - 1

    elif expr[0] == "=":
        tensor = expr[1]
        value_expr = expr[2]
        depth = expr[3]
        idx = []
        for i in range(len(tensor.shape)):
            if depth:
                didx = ["I{}_{}".format(i, depth)]
            else:
                didx = ["i{}".format(i)]
            for j in range(i+1,len(tensor.shape)):
                didx.append("{}".format(tensor.shape[j]))
            idx.append("*".join(didx))
        idx = " + ".join(idx)
        output.write(" "*(indent+1)*intent_spaces)
        output.write("{name}[{idx}] = ".format(name=tensor.name, idx=idx))
        output.write(gen_c_expr(value_expr, output, indent=indent+1))
        output.write(";\n")
        return indent

    elif expr[0] == "idx":
        if expr[2]==0:
            return f"i{expr[1]}"
        else:
            return f"I{expr[1]}_{expr[2]}"

    elif expr[0] == "def":
        output.write("#define ")
        output.write(gen_c_expr(expr[1], output, indent=0))
        output.write(" ")
        output.write("(")
        output.write(gen_c_expr(expr[2], output, indent=0))
        output.write(")")
        output.write("\n")

    elif expr[0] == "undef":
        output.write("#undef ")
        output.write(gen_c_expr(expr[1], output, indent=0))
        output.write("\n")

    elif expr[0] == "ref":
        a = gen_c_expr(expr[1], output, indent=0)
        b = gen_c_expr(expr[2], output, indent=0)
        return f"{a}[{b}]"

    elif expr[0] == "+":
        args = [gen_c_expr(e, output, indent=0) for e in expr[1]]
        return "".join(["(", "+".join(args), ")"])

    elif expr[0] == "-":
        args = [gen_c_expr(e, output, indent=0) for e in expr[1]]
        return "".join(["(", "-".join(args), ")"])

    elif expr[0] == "*":
        args = [gen_c_expr(e, output, indent=0) for e in expr[1]]
        return "".join(["(", "*".join(args), ")"])

    elif expr[0] == "//":
        # XXX float args
        args = [gen_c_expr(e, output, indent=0) for e in expr[1]]
        return "".join(["(", "/".join(args), ")"])

    elif expr[0] == "%":
        args = [gen_c_expr(e, output, indent=0) for e in expr[1]]
        return "".join(["(", "%".join(args), ")"])

    elif expr[0] == "term":
        return str(expr[1])

    elif expr[0] == "func":
        out = expr[1]
        params = expr[2]
        output.write(" "*indent*intent_spaces)
        args = [f"{out.dtype} * {out.name}"]
        for p in params:
            args.append(f"{p.dtype} * {p.name}")
        output.write("void gen_{}({})\n".format(out.name, ", ".join(args)))

        output.write(" "*indent*intent_spaces)
        output.write("{\n")
        return indent + 1

    elif expr[0] == "endfunc":
        output.write(" "*(indent-1)*intent_spaces)
        output.write("}\n\n")
        return indent - 1

    else:
        raise NotImplementedError("Unknown expr op {}".format(expr[0]))

def gen_func(ctx, output):
    output.write("#include <stdio.h>\n");
    output.write("#include <math.h>\n");
    output.write("\n")

    if ctx["data"]:
        output.write("// Data\n");
    for sym_name in ctx["data"]:
        dtype, data = ctx["data"][sym_name]
        array = False
        output.write("{dtype} {name}".format(dtype=dtype, name=sym_name));
        output.write("[] = {")
        output.write(",".join([str(x) for x in data]))
        output.write("};\n");
    if ctx["data"]:
        output.write("\n");

    indent = 0
    for expr in ctx["stmt"]:
        indent = gen_c_expr(expr, output, indent)

