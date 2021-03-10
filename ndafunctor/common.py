def ranger(rg):
    import itertools
    return itertools.product(*[range(base,base+num*step,step) for base,num,step in rg])

def rangel(a):
    return range(len(a))