import subprocess

def draw_graph(functor):
    def walk(f, functor):
        f.write(f"\t{functor.get_name()}\n")
        for s in functor.subs:
            f.write(f"\t{s.get_name()} -> {functor.get_name()} [label=\"{functor.opdesc}\"];\n")
            walk(f, s)

    tmp = functor.get_tmp()
    dotfile = tmp+".dot"
    pngfile = tmp+".png"
    with open(dotfile, "w") as f:
        f.write("digraph G {\n")
        walk(f, functor)
        f.write("}\n")

    subprocess.check_output(["dot", dotfile, "-Tpng", "-o", pngfile])
    print(pngfile)
