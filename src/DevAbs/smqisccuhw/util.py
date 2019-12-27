
def logit(fn):
    def __inner__(*a, **k):
        print("{}: {} {}".format(fn.__name__, a, k))
        return fn(*a, **k)
    return __inner__


