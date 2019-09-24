import logging
import pathlib
import shutil

import ceryle.util as util
from ceryle.commands.executable import Executable, ExecutionResult

logger = logging.getLogger(__name__)


class Copy(Executable):
    def __init__(self, src, dst, glob=None):
        self._src = util.assert_type(src, str, pathlib.Path)
        self._dst = util.assert_type(dst, str, pathlib.Path)
        self._glob = util.assert_type(glob, None, str)

    def execute(self, *args, context=None, **kwargs):
        srcpath = pathlib.Path(context, self._src)
        dstpath = pathlib.Path(context, self._dst)

        if not srcpath.exists():
            util.print_err(f'copy source not found: {self._src}')
            return ExecutionResult(1)

        if self._glob:
            logger.info(f'copying file(s) {self._src} to {self._dst} (glob: {self._glob})')
            _copy_glob(srcpath, dstpath, self._glob)
        else:
            logger.info(f'copying file(s) {self._src} to {self._dst}')
            _copy_internal(srcpath, dstpath)
        return ExecutionResult(0)

    def __str__(self):
        return f'copy(src={self._src}, dst={self._dst}, glob={self._glob})'


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


def _copy_glob(srcpath, dstpath, pattern):
    for p in srcpath.glob(pattern):
        d = dstpath.joinpath(p.relative_to(srcpath))
        _copy_internal(p, d)
