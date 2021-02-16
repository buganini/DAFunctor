from .tensor import *

intent_spaces = 4

def gen_c_expr(expr, output, indent=0):
    if type(expr) is str:
        output.write(expr)
        return

    if expr[0] == "for":
        shape = expr[1]
        output.write(" "*indent*intent_spaces)
        output.write("int idx[{}];\n".format(len(shape)))
        for i in range(len(shape)):
            output.write(" "*indent*intent_spaces)
            output.write("{}for(idx[{i}]=0;idx[{i}]<{n};idx[{i}]++)\n".format(" "*i*2, i=i, n=shape[i]))
        output.write("{\n")

    elif expr[0] == "endfor":
        output.write(" "*indent*intent_spaces)
        output.write("}\n")

    elif expr[0] == "=":
        if type(expr[1]) is ITensor:
            tensor = expr[1]
            idx = []
            for i in range(len(tensor.shape)):
                didx = ["idx[{}]".format(i)]
                for j in range(i+1,len(tensor.shape)):
                    didx.append("{}".format(tensor.shape[j]))
                idx.append("*".join(didx))
            idx = " + ".join(idx)
            output.write(" "*(indent+1)*intent_spaces)
            output.write("{name}[{idx}] = ".format(name=tensor.name, idx=idx))
            gen_c_expr(expr[2], output, indent=indent+1)
            output.write(";\n")

    elif expr[0] == "ref":
        gen_c_expr(expr[1], output, indent=0)
        output.write("[")
        gen_c_expr(expr[2], output, indent=0)
        output.write("]")

    elif expr[0] == "+":
        output.write("(")
        gen_c_expr(expr[1], output, indent=0)
        output.write("+")
        gen_c_expr(expr[2], output, indent=0)
        output.write(")")

    elif expr[0] == "term":
        output.write(expr[1])

    else:
        raise NotImplementedError("Unknown expr op {}".format(expr[0]))

def gen_c(ctx, output, indent=0):
    if ctx["symbols"]:
        output.write("// Tensors\n");
    for sym_name in ctx["symbols"]:
        dtype, shape = ctx["symbols"][sym_name]
        size = 1
        for s in shape:
            size *= s
        output.write("{dtype} {name}[{size}];\n".format(dtype=dtype, name=sym_name, size=size));
    if ctx["symbols"]:
        output.write("\n")


    if ctx["data"]:
        output.write("// Data\n");
    for sym_name in ctx["data"]:
        dtype, data = ctx["data"][sym_name]
        array = False
        if type(data) is list:
            array = True
        output.write("{dtype} {name}".format(dtype=dtype, name=sym_name));
        if array:
            output.write("[] = {")
            output.write(",".join([str(x) for x in data]))
            output.write("};\n");
        else:
            output.write("= {};\n".format(data))
    if ctx["data"]:
        output.write("\n");

    for expr in ctx["cfg"]:
        gen_c_expr(expr, output, indent=indent)