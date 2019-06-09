import ast
import pathlib

from ceryle.const import DEFAULT_TASK_FILE


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


def find_task_file(start):
    def dirs():
        wd = pathlib.Path(start).absolute()
        yield wd
        for p in wd.parents:
            yield p

    for d in dirs():
        t = pathlib.Path(d, DEFAULT_TASK_FILE)
        if t.exists():
            return str(t)
    return None
