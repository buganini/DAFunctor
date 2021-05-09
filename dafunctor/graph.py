import subprocess
from PIL import Image

def draw_graph(functors, output, display=False):
    def walk(f, functor):
        if hasattr(functor, "_display"):
            return
        functor._display = True
        f.write(f"\t{functor.get_name()} [label=\"{functor.get_name()}\n{functor.shape.get_desc()}\"];\n")
        for s in functor.subs:
            f.write(f"\t{s.get_name()} -> {functor.get_name()} [label=\"{functor.opdesc}\"];\n")
            walk(f, s)

    dotfile = output+".dot"
    pngfile = output+".png"
    with open(dotfile, "w") as f:
        f.write("digraph G {\n")
        for functor in functors:
            walk(f, functor)
        f.write("}\n")

    subprocess.check_output(["dot", dotfile, "-Tpng", "-o", pngfile])

    if display:
        Image.open(pngfile).show()
    return pngfile
