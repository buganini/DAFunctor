import ast
import inspect

# https://github.com/RyanKung/assign

def gen_assign_checker_ast(node):
    targets = [t.id for t in node.targets]
    obj_name = node.value.id

    return ast.If(
        test=ast.Call(
            func=ast.Name(id='hasattr', ctx=ast.Load()),
            args=[
                ast.Name(id=obj_name, ctx=ast.Load()),
                ast.Str(s='__assign__'),
            ],
            keywords=[],
            starargs=None,
            kwargs=None
        ),
        body=[
            ast.Assign(
                targets=[ast.Name(id=target, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=obj_name, ctx=ast.Load()),
                        attr='__assign__',
                        ctx=ast.Load()
                    ),
                    args=[ast.Str(s=target)],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                )
            )
            for target in targets],
        orelse=[]
    )

class AssignTransformer(ast.NodeTransformer):
    def generic_visit(self, node):
        ast.NodeTransformer.generic_visit(self, node)
        return node

    def visit_Assign(self, node):
        if not isinstance(node.value, ast.Name):
            return node
        new_node = gen_assign_checker_ast(node)
        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
        return new_node

def patch_func(func):
    if func.__code__.co_filename == "__assign__":
        return func
    import re
    trans = AssignTransformer()
    src = inspect.getsource(func)
    src = src.rstrip("\r\n").split("\n")
    spaces = min([len(re.match(r" *", l)[0]) for l in src])
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
        def __assign__(self, name):
            print("assign", name)

    @assign
    def f(a):
        var_name = a
        return var_name

    f(A())
