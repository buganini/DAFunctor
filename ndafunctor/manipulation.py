from .functor import Functor

def transpose(functor, dims):
    rmap = [dims.index(i) for i in range(len(functor.shape))]
    iexpr = [["i{}".format(axis)] for axis in rmap]
    dexpr = [functor]
    shape = [functor.shape[dims[i]] for i in range(len(functor.shape))]
    return Functor(
        shape,
        dexpr = dexpr,
        iexpr = iexpr,
        desc = "transposed_{}".format(functor.desc)
    )
