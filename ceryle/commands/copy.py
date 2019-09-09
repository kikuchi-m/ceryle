import pathlib
import shutil

import ceryle.util as util
from ceryle.commands.executable import Executable, ExecutionResult


class Copy(Executable):
    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def execute(self, *args, context=None, **kwargs):
        srcpath = pathlib.Path(context, self._src)
        dstpath = pathlib.Path(context, self._dst)

        if not srcpath.exists():
            util.print_err(f'copy source not found: {self._src}')
            return ExecutionResult(1)

        _copy_internal(srcpath, dstpath)
        return ExecutionResult(0)

    def __str__(self):
        return f'copy(src={self._src}, dst={self._dst})'


def _copy_internal(srcpath, dstpath):
    if srcpath.is_dir():
        if dstpath.exists():
            for s in srcpath.iterdir():
                _copy_internal(s, dstpath.joinpath(s.name))
        else:
            shutil.copytree(srcpath, dstpath, copy_function=shutil.copyfile)
    else:
        _copy_file(srcpath, dstpath)


def _copy_file(srcpath, dstpath):
    if not dstpath.exists() and not dstpath.parent.exists():
        dstpath.parent.mkdir(parents=True)
    if dstpath.is_dir():
        dst = dstpath.joinpath(srcpath.name)
    else:
        dst = dstpath
    shutil.copyfile(srcpath, dst)
