from collections import OrderedDict
from .common import *
from .expression import *
from .graph import *
import re

class CFG():
    def __init__(self, parent=None, data=None):
        self.parent = parent
        if parent is None:
            self.depth = -2
        else:
            self.depth = parent.depth + 1
        self.data = data
        if self.data is None:
            self.data = OrderedDict()
        self.stmt = []
        self.output = False
        self.header = 0

    def __repr__(self):
        return str(self.stmt)

    def __str__(self):
        return self.__repr__()

    def append(self, stmt):
        self.stmt.append(stmt)

    def append_header(self, stmt):
        self.stmt.insert(self.header, stmt)
        self.header += 1

    def enter(self, init=None, header=None):
        scope = CFG(parent=self, data=self.data)
        self.append(["scope", scope])
        if not header is None:
            scope.append_header(header)
        if not init is None:
            scope.append(init)
        return scope

    def print(self):
        import pprint
        pp = pprint.PrettyPrinter()
        pp.pprint(self.stmt)

def build_cfg(ctx, path):
    value = None
    scope = ctx
    idepth = 0
    rg, phases = path
    for depth, (functor, sidx) in enumerate(phases):
        if depth == 0:
            out = phases[-1][0]
            if not out._daf_is_output and not out._daf_is_declared:
                out._daf_is_declared = True
                scope.append_header(["autobuf", out])
            scope.append(["for_shape", rg, scope.depth + 1, idepth])
            scope = scope.enter()

        if functor._daf_exported: # XXX: exported symbol
            value = gen_base_expr(functor)
        else:
            if functor.partitions:
                if functor.iexpr:
                    scope.append(["comment", functor.opdesc])
                    for d,iexpr in enumerate(functor.iexpr):
                        scope.append(["val","i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), sidx, functor.subs[sidx], idepth, value)])
                    scope.append(["newline"])
                    idepth += 1
            else:
                if functor.iexpr:
                    scope.append(["comment", functor.opdesc])
                    for d,iexpr in enumerate(functor.iexpr):
                        scope.append(["val", "i", ["idx", d, scope.depth, idepth+1], build_ast(scope, Expr(iexpr), sidx, functor.subs[sidx], idepth, value)])
                    scope.append(["newline"])
                    idepth += 1
                value = build_ast(scope, Expr(functor.vexpr), sidx, functor, idepth, value)

        final_out = depth + 1 == len(phases)
        if not functor.sexpr is None: # scatter
            val = ["v", scope.depth]
            scope.append(["val", phases[-1][0].get_type(), val, value])
            scope.append(["for_scatter", functor.shape, functor.sexpr, scope.depth + 1, idepth])
            scope = scope.enter()
            value = val
        if final_out:
            if value is None:
                print("Path", path)
                raise AssertionError("value is None")
            scope.append(["=", functor, value, idepth, scope.depth])

def gen_base_expr(functor):
    axis = []
    for i in rangel(functor.shape):
        axis.append(["*", [f"i{i}"]+[s for s in functor.shape[i+1:]]])

    return ["ref", functor.get_name(), ["+", axis]]

def build_ast(ctx, expr, sidx, functor, depth, value):
    op = expr.op
    if type(op) in (int, float):
        return op
    elif op in ("+","-","*","//","/","%"):
        args = [build_ast(ctx, e, sidx, functor, depth, value) for e in expr]
        return [op, args]
    elif op == ">":
        gt_a = build_ast(ctx, expr[0], sidx, functor, depth, value)
        gt_b = build_ast(ctx, expr[1], sidx, functor, depth, value)
        return [">", gt_a, gt_b]
    elif op == "?:":
        ie_cond = build_ast(ctx, expr[0], sidx, functor, depth, value)
        ie_if = build_ast(ctx, expr[1], sidx, functor, depth, value)
        ie_else = build_ast(ctx, expr[2], sidx, functor, depth, value)
        return ["?:", ie_cond, ie_if, ie_else]
    elif op == "ref":
        ref_a = build_ast(ctx, expr[0], sidx, functor, depth, value)
        ref_b = build_ast(ctx, expr[1], sidx, functor, depth, value)
        if type(ref_b) is list:
            ref_b = tuple(ref_b)
        return ["ref", ref_a, ref_b]
    elif op == "si":
        return sidx
    elif op == "d":
        name = functor.data.get_name()
        ctx.data[name] = (functor.data.get_type(), functor.data)
        return name
    elif re.match("-?[0-9]+", op):
        return ["term",op]
    elif re.match("d[0-9]+", op):
        i = int(op[1:])
        return ["term", functor.data[i]]
    elif re.match("i[0-9]+", op):
        return ["idx", int(op[1:]), ctx.depth, depth]
    elif re.match("v[0-9]+", op):
        i = int(op[1:])
        sub = functor.subs[i]
        if sub._daf_exported:
            return gen_base_expr(sub)
        elif not sub.vexpr is None:
            return build_ast(ctx, Expr(sub.vexpr), i, sub, depth, value)
        else:
            if value is None:
                print(f"subs[{i}]", sub)
                raise AssertionError()
            return value
    elif op == "buf":
        return gen_base_expr(functor)
    else:
        raise NotImplementedError("Invalid token {}".format(op))

def request_export(functor):
    functor._daf_requested_contiguous = True
    functor._daf_is_output = True

def mark_contiguous_request(functor):
    if functor.daf_is_joiner():
        for f in functor.subs:
            if f._daf_group != functor._daf_group:
                f._daf_requested_contiguous = True
    for f in functor.subs:
        mark_contiguous_request(f)

def shape_grouping(functor, group=None):
    if functor._daf_group is None:
        functor.daf_set_group(group)
    if functor.daf_is_joiner():
        m = {}
        for f in functor.subs:
            if not f._daf_is_contiguous:
                k = tuple(f.shape)
                if not k in m:
                    m[k] = []
                m[k].append(f)
        for k in m:
            if k == tuple(functor.shape):
                for f in m[k]:
                    shape_grouping(f, functor._daf_group)
            else:
                g = Group()
                for f in m[k]:
                    shape_grouping(f, g)
    else:
        for f in functor.subs:
            if not f._daf_is_contiguous:
                shape_grouping(f, functor._daf_group)


def strip_tail_reshape(functor, derived=None):
    from .manip import reshape
    from .functor import Reshaper
    if functor.src_func == reshape:
        cur = functor
        while cur.src_func == reshape:
            cur = cur.subs[0]
        if cur.daf_is_contiguous():
            reshaper = Reshaper(cur, functor.shape)
            functor.subs[0] = reshaper
            functor.iexpr = None
            if derived:
                for i in rangel(derived.subs):
                    if derived.subs[i] is functor:
                        derived.subs[i] = reshaper
                        break
    else:
        for s in functor.subs:
            strip_tail_reshape(s, functor)

def split_graph(functor):
    seq = []
    for f in functor.subs:
        seq.extend(split_graph(f))
    if functor._daf_requested_contiguous and not functor._daf_is_contiguous:
        seq.append(functor)

    return list_dedup(seq)

def tailor_shape(paths):
    """
    Tailor "seed index" according to functors
    """
    def idx_in_range(idx, srg):
        if len(idx) != len(srg):
            raise AssertionError(f"Dimension mismatch {idx} {srg}")
        if not all([i>=r[0] for i,r in zip(idx, srg)]):
            return False
        if not all([i<r[0]+r[1]*r[2] for i,r in zip(idx, srg)]):
            return False
        if not all([(i-r[0]) % r[2] == 0 for i,r in zip(idx, srg)]):
            return False
        return True

    ret = []
    for brg, phases in paths:
        # fast pass
        not_partitioned = all([x[0].partitions is None or len(x[0].partitions)==1 for x in phases])
        same_size = len(set([x[0].shape.size() for x in phases])) == 1
        if same_size and not_partitioned:
            ret.append((brg, phases))
            continue

        # slow check
        vs = [set() for i in rangel(brg)]

        for idx in ranger(brg):
            cidx = idx
            in_range = True

            for i, (functor, sidx) in enumerate(phases):
                if functor.partitions and i > 0:
                    if not idx_in_range(idx, functor.partitions[sidx]):
                        in_range = False
                        break

                pidx = functor.eval_index(idx, sidx)

                if pidx is None:
                    in_range = False
                    break

                idx = pidx

            if in_range:
                for i,c in enumerate(cidx):
                    vs[i].add(c)

        # slices generation
        vs = [sorted(list(v)) for v in vs]
        num = [len(v) for v in vs]
        if all([n > 0 for n in num]):
            base = [min(v) for v in vs]
            step = [v[1]-v[0] if len(v) > 1 else 1 for v in vs]
            rg = list(zip(base, num, step))
            ret.append((rg, phases))
    return ret

def build_blocks(functor, target):
    """
    Translate graph to ("seed index", [("functor", "sub-functor selector")])
    """
    paths = []
    rg = functor.shape.shape

    if functor is target or not functor.daf_is_contiguous():
        if functor.partitions:
            for i,_ in enumerate(functor.partitions):
                for brg,bpath in build_blocks(functor.subs[i], target):
                    paths.append((brg, bpath+[(functor, i)]))
        elif not functor.daf_is_joiner():
            for i in rangel(functor.subs):
                for brg,bpath in build_blocks(functor.subs[i], target):
                    paths.append((brg, bpath+[(functor, i)]))

    if not paths:
        paths.append((rg, [(functor, 0)]))

    return paths

def transpile(ctx, nodes, visualize=None, display=False):
    # mark export node
    for n in nodes:
        request_export(n)

    for n in nodes:
        shape_grouping(n)

    # mark shared node
    for n in nodes:
        mark_contiguous_request(n)

    # reshape optimization
    for n in nodes:
        strip_tail_reshape(n)

    if visualize:
        draw_graph(nodes, visualize, display)

    graphs = []
    for n in nodes:
        graphs.extend(split_graph(n))

    graphs = list_dedup(graphs)
    # print("graphs", [x.id for x in graphs])
    for graph in graphs:
        paths = build_blocks(graph, graph)
        paths = tailor_shape(paths)
        if not paths:
            continue
        for path in paths:
            # print("path", path[0], [f"#{x[0].id}" for x in path[1]])
            functor = path[1][-1][0]
            build_cfg(ctx, path)
        if not functor._daf_is_output:
            ctx.append(["newline"])
            ctx.append(["comment", f"end of {functor.get_name()}"])
            ctx.append(["newline"])
        graph._daf_exported = True
