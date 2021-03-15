def greater(cls, a, b):
    return cls(
        a.shape,
        dtype = "b",
        vexpr = ["?:", [[">",["v0","v1"]], 1, 0]],
        subs = [a, b],
        opdesc = "greater",
        desc = "greater",
    )