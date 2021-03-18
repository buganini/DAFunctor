import ast
import inspect

def gen_assign_checker_ast(node):
    exprs = [node]
    todo = list(node.targets)
    while todo:
        target = todo.pop(0)
        if type(target) is ast.Tuple:
            todo.extend(target.elts)
            continue
        if type(target) is ast.Name:
            target_load = ast.Name(id=target.id, ctx=ast.Load())
            assign_name = ast.Str(s=target.id)
            assign_slice = ast.Constant(value=None, kind=None)
        elif type(target) is ast.Subscript:
            target_load = ast.Subscript(value=target.value, slice=target.slice, ctx=ast.Load())
            assign_name = ast.Str(s=target.value.id)
            # print(ast.dump(target))
            if type(target.slice) is ast.Index:
                assign_slice = target.slice.value
            else:
                assign_slice = target.slice
        else:
            print(ast.dump(target))
            raise AssertionError()
        exprs.append(ast.If(
            test=ast.Call(
                func=ast.Name(id='hasattr', ctx=ast.Load()),
                args=[
                    target_load,
                    ast.Str(s='__assign__'),
                ],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            body=[
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=target_load,
                            attr='__assign__',
                            ctx=ast.Load()
                        ),
                        args=[assign_name, assign_slice],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    )
                )
            ],
            orelse=[]
        ))


    return ast.If(
        test=ast.Constant(value=True),
        body=exprs,
        orelse=[]
    )

class AssignTransformer(ast.NodeTransformer):
    def generic_visit(self, node):
        ast.NodeTransformer.generic_visit(self, node)
        return node

    def visit_Assign(self, node):
        new_node = gen_assign_checker_ast(node)
        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
        # print(ast.dump(new_node))
        # print(ast.unparse(new_node))
        return new_node

def patch_func(func):
    if func.__code__.co_filename == "__assign__":
        return func
    import re
    trans = AssignTransformer()
    src = inspect.getsource(func)
    src = src.rstrip("\r\n").split("\n")
    spaces = [x for x in [len(re.match(r" *", l)[0]) for l in src] if x != 0]
    if spaces:
        spaces = min(spaces)
    else:
        spaces = 0
    src = "\n".join([l[spaces:] for l in src])
    node = ast.parse(src)
    new_node = trans.visit(node)
    ast.fix_missing_locations(new_node)
    patched_code = compile(new_node, "__assign__", "exec")
    exec(patched_code)
    return locals()[func.__name__]


if __name__=="__main__":
    def assign(func):
        patched_func = patch_func(func)
        def f(*args, **kwargs):
            ret = patched_func(*args, **kwargs)
        return f

    class A():
        def __assign__(self, name, idx):
            print("Assign", self, "as", name, "idx", idx)

    @assign
    def f(assignee):
        a = assignee

        b, c = assignee, assignee

        arr = [assignee,assignee]
        d, e = arr

        f, (g, h) = assignee, (assignee,assignee)

        i = [0,0]
        i[1] = assignee

        j = [0,0]
        x = 1
        j[x] = assignee

        k = [0,0]
        x = [1]
        z = 0
        k[x[z]] = assignee

        print("a", repr(a))
        print("b", repr(a))
        print("c", repr(a))
        print("d", repr(a))
        print("e", repr(a))
        print("f", repr(a))
        print("g", repr(a))
        print("h", repr(a))
        print("i", repr(a))
        print("j", repr(a))
        print("k", repr(a))

    f(A())
