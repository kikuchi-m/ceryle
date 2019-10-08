import logging
import os
import pathlib

import ceryle.util as util
from ceryle.commands.executable import Executable, ExecutionResult

logger = logging.getLogger(__name__)


class Remove(Executable):
    def __init__(self, *targets):
        self._targets = [util.assert_type(t, str, pathlib.Path) for t in targets]

    def execute(self, *args, context=None, **kwargs):
        for target in self._targets:
            if not _remove(pathlib.Path(context, target)):
                return ExecutionResult(1)
        return ExecutionResult(0)

    def __str__(self):
        files = ', '.join([str(f) for f in self._targets])
        return f'remove({files})'


def _remove(target):
    if not target.exists():
        return True
    if target.is_symlink():
        logger.debug(f'remove symlink: {target}')
        target.unlink()
        return True
    if target.is_dir():
        for t in target.iterdir():
            if not _remove(t):
                logger.warn(f'failed to remove {t}')
                return False
        logger.debug(f'remove directory: {target}')
        target.rmdir()
        return True
    if target.is_file():
        logger.debug(f'remove file: {target}')
        os.remove(target)
        return True
