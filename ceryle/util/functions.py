import ast
import logging
import pathlib

from ceryle.const import DEFAULT_TASK_FILE, CERYLE_DIR, CERYLE_TASK_DIR, CERYLE_TASK_EXT
from ceryle.const import CERYLE_EX_DIR, CERYLE_EX_FILE_EXT

logger = logging.getLogger(__name__)


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
    logger.debug(f'find task file from {start}')

    def dirs():
        wd = pathlib.Path(start).absolute()
        yield wd
        for p in wd.parents:
            yield p

    for d in dirs():
        t = pathlib.Path(d, DEFAULT_TASK_FILE)
        if t.is_file():
            return str(t)
    return None


def collect_task_files(start):
    home = pathlib.Path.home().joinpath(CERYLE_DIR, CERYLE_TASK_DIR)
    files = _rglob_files(home, CERYLE_TASK_EXT)

    default_task_file = find_task_file(start)
    if default_task_file:
        logger.debug(f'task file found: {default_task_file}')
        files.append(default_task_file)

        root_dir = pathlib.Path(default_task_file).parent.joinpath(CERYLE_DIR, CERYLE_TASK_DIR)
        files = [
            *files,
            *_rglob_files(root_dir, CERYLE_TASK_EXT)
        ]

    return files, default_task_file and str(pathlib.Path(default_task_file).parent)


def collect_extension_files(start):
    home = pathlib.Path.home().joinpath(CERYLE_DIR, CERYLE_EX_DIR)
    ex_files = _rglob_files(home, CERYLE_EX_FILE_EXT)

    default_task_file = find_task_file(start)
    if default_task_file:
        ex_dir = pathlib.Path(default_task_file).parent.joinpath(CERYLE_DIR, CERYLE_EX_DIR)
        ex_files = [
            *ex_files,
            *_rglob_files(ex_dir, CERYLE_EX_FILE_EXT)
        ]

    return ex_files


def _rglob_files(p, ext):
    return sorted([str(p) for p in p.rglob('*' + ext)])
