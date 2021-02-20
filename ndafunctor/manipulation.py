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
