import inspect


def invalidtypes(*args):
    message = 'unexpected input types:'
    for arg in args:
        message += type(arg)
    raise ValueError(message)

def islambda(test, args):
    if isinstance(test, type(lambda: 0)) and isinstance(args, int):
        return len(inspect.signature(test).parameters) == args
    return False;