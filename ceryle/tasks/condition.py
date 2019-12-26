import logging

import ceryle.commands.builtin as builtin
import ceryle.util as util

from ceryle.commands.executable import Executable

logger = logging.getLogger(__name__)


class Condition:
    WIN = util.is_win()
    LINUX = util.is_linux()
    MAC = util.is_mac()
    NO_INPUT = builtin.no_input()
    HAS_INPUT = builtin.has_input()
    all = builtin.execute_all
    any = builtin.execute_any
    fail = builtin.expect_fail
    expression = builtin.expression

    def __init__(self, condition):
        self._condition = util.assert_type(condition, Executable, bool)
        # self._context = util.assert_type(context, str)
        logger.debug(f'condition: {self._condition}')

    def test(self, context=None, inputs=[], dry_run=False):
        logger.info(f'testing {self._condition}')
        logger.debug(f'context: {context}')
        logger.debug(f'inputs: {inputs}')
        if isinstance(self._condition, bool):
            return dry_run or self._condition
        return dry_run or self._test_executable(context=context, inputs=inputs)

    def _test_executable(self, context=None, inputs=[]):
        res = self._condition.execute(context=context, inputs=inputs)
        return res.return_code == 0

    def _no_input(self, inputs=[]):
        return not self._has_input(inputs=inputs)

    def _has_input(self, inputs=[]):
        return len(inputs) > 0
