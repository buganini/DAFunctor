import subprocess
from PIL import Image

def draw_graph(functors, output, display=False):
    def walk(ctx, functor):
        if hasattr(functor, "_display"):
            return
        functor._display = True
        attrs = {
            "label": f'"{functor.get_name()}\\n{functor.shape.get_desc()}"',
            "peripheries": [1,2][functor.daf_is_contiguous()],
        }
        attrs = "".join([f"{k}={attrs[k]};" for k in attrs])

        if functor._daf_group:
            g = functor._daf_group.id
            if not g in ctx["subgraph"]:
                ctx["subgraph"][g] = []
            ctx["subgraph"][g].append(f"{functor.get_name()} [{attrs}]")
        else:
            ctx["node"].append(f"{functor.get_name()} [{attrs}]")
        for s in functor.subs:
            ctx["edge"].append(f"{s.get_name()} -> {functor.get_name()} [label=\"{functor.opdesc}\"]")
            walk(ctx, s)

    ctx = {
        "node": [],
        "edge": [],
        "subgraph": {}
    }

    for functor in functors:
        walk(ctx, functor)

    dotfile = output+".dot"
    pngfile = output+".png"
    with open(dotfile, "w") as f:
        f.write("digraph G {\n")
        for g in ctx["subgraph"]:
            f.write(f"    subgraph cluster_{g} {{\n")
            for l in ctx["subgraph"][g]:
                f.write(f"        {l};\n")
            f.write("        color=blue;\n");
            f.write(f"    }}\n")

            for l in ctx["node"]:
                f.write(f"    {l};\n")
            f.write("\n");

            for l in ctx["edge"]:
                f.write(f"    {l};\n")
        f.write("}\n")

    subprocess.check_output(["dot", dotfile, "-Tpng", "-o", pngfile])

    if display:
        Image.open(pngfile).show()
    return pngfile
