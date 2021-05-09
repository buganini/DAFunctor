import subprocess
from PIL import Image

def draw_graph(functor, display=False):
    def walk(f, functor):
        f.write(f"\t{functor.get_name()} [label=\"{functor.get_name()}\n{functor.shape.get_desc()}\"];\n")
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

    if display:
        Image.open(pngfile).show()
    return pngfile
