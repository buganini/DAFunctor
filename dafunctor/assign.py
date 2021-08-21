import ast
import inspect

# Tested with:
# * 3.8
# * 3.9

class AssignTransformer(ast.NodeTransformer):
    def generic_visit(self, node):
        ast.NodeTransformer.generic_visit(self, node)
        return node

    def visit_Assign(self, node):
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
                            starargs=None,
                            keywords=[],
                            kwargs=None
                        )
                    )
                ],
                orelse=[]
            ))


        new_node = ast.If(
            test=ast.Constant(value=True),
            body=exprs,
            orelse=[]
        )

        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
        # print(ast.dump(new_node))
        # print(ast.unparse(new_node))

        return new_node

    def visit_FunctionDef(self, func):
        for i,arg in enumerate(func.args.args):
            assign = ast.If(
                test=ast.Call(
                    func=ast.Name(id='hasattr', ctx=ast.Load()),
                    args=[
                        ast.Name(id=arg.arg, ctx=ast.Load()),
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
                                value=ast.Name(id=arg.arg, ctx=ast.Load()),
                                attr='__assign__',
                                ctx=ast.Load()
                            ),
                            args=[ast.Str(s=arg.arg), ast.Constant(value=None, kind=None)],
                            keywords=[],
                            starargs=None,
                            kwargs=None
                        )
                    )
                ],
                orelse=[]
            )
            func.body.insert(i, assign)
        ast.NodeTransformer.generic_visit(self, func)
        return func

def patch_func(func, global_vars=None):
    if func.__code__.co_filename == "__assign__":
        return func
    import re
    trans = AssignTransformer()
    src = inspect.getsource(func)
    src = src.rstrip("\r\n").split("\n")
    spaces = [x for x in [len(re.match(r" *", l)[0]) for l in src if l]]
    if spaces:
        spaces = min(spaces)
    else:
        spaces = 0
    src = "\n".join([l[spaces:] for l in src])
    node = ast.parse(src)
    # print(ast.dump(node))
    new_node = trans.visit(node)
    # print(ast.unparse(new_node))
    ast.fix_missing_locations(new_node)
    patched_code = compile(new_node, "__assign__", "exec")
    local_vars = {}
    exec(patched_code, global_vars, local_vars)
    return local_vars[func.__name__]

def patch_assign(func):
    patched_func = patch_func(func, inspect.stack()[1].frame.f_globals)
    def f(*args, **kwargs):
        ret = patched_func(*args, **kwargs)
    return f

if __name__=="__main__":
    class A():
        def __assign__(self, name, idx):
            print("Assign", self, "as", name, "idx", idx)

    @patch_assign
    def f(assignee):
        a = assignee

        b, c = assignee, assignee

        arr = [assignee, assignee]
        d, e = arr

        f, (g, h) = assignee, (assignee, assignee)

        i = [0,0]
        i[1] = assignee

        j = [0,0]
        x = 1
        j[x] = assignee

        k = [0,0]
        x = [1]
        z = 0
        k[x[z]] = assignee

        # l = list(range(10))
        # l[2:3] = assignee

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
