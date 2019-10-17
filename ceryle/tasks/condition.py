import logging

import ceryle.commands.buildin as buildin
import ceryle.util as util

from ceryle.commands.executable import Executable

logger = logging.getLogger(__name__)


class Condition:
    NO_INPUT = buildin.no_input()
    HAS_INPUT = buildin.has_input()
    all = buildin.execute_all
    any = buildin.execute_any
    expression = buildin.expression

    def __init__(self, condition, context):
        self._condition = util.assert_type(condition, Executable)
        self._context = util.assert_type(context, str)
        logger.debug(f'condition: {self._condition}')

    def test(self, inputs=[], dry_run=False):
        logger.info(f'testing {self._condition}')
        logger.debug(f'context: {self._context}')
        logger.debug(f'inputs: {inputs}')
        return dry_run or self._test_executable(inputs=inputs)

    def _test_executable(self, inputs=[]):
        res = self._condition.execute(context=self._context, inputs=inputs)
        return res.return_code == 0

    def _no_input(self, inputs=[]):
        return not self._has_input(inputs=inputs)

    def _has_input(self, inputs=[]):
        return len(inputs) > 0
