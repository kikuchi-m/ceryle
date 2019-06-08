import ast


def getin(d, *keys, default=None):
    if not keys:
        return d

    k = keys[0]
    if not isinstance(d, dict) or k not in d:
        return default
    return getin(d[k], *keys[1:], default=default)


def parse_to_ast(f):
    with open(f) as fp:
        code = fp.read()
        return compile(code, f, 'exec', ast.PyCF_ONLY_AST)
