from .functor import Functor

def transpose(functor, dims):
    iexpr = [["i{}".format(axis)] for axis in dims]
    shape = [functor.shape[dims[i]] for i in range(len(functor.shape))]
    return Functor(
        shape,
        iexpr = iexpr,
        desc = "transposed_{}".format(functor.desc),
        subs = [functor]
    )

def stack(array, axis=0):
    iexpr = [["i{}".format(i) for i in range(len(array[0].shape))]]
    iexpr.insert(axis, [0])
    shape = list(array[0].shape)
    shape.insert(axis, list(range(1,len(array)+1)))
    return Functor(
        shape,
        iexpr = iexpr,
        desc = "stack_{}".format(axis),
        subs = array
    )

def expand_dims(a, axis):
    iexpr = [["i{}".format(i) for i in range(len(a.shape))]]
    iexpr.insert(axis, [0])
    shape = list(a.shape)
    shape.insert(axis, 1)
    return Functor(
        shape,
        iexpr = iexpr,
        desc = "expand_dims_{}_{}".format(axis, a.desc),
        subs = [a]
    )
