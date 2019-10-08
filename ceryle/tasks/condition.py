import logging

import ceryle.commands.buildin as buildin
import ceryle.util as util

from ceryle.commands.executable import Executable

logger = logging.getLogger(__name__)


class Condition:
    NO_INPUT = 'no_input'
    HAS_INPUT = 'has_input'
    expression = buildin.expression

    def __init__(self, condition, context):
        self._condition, self._test_fun = assert_condition(condition)
        self._context = util.assert_type(context, str)
        logger.debug(f'condition: {self._condition}')

    def test(self, inputs=[], dry_run=False):
        logger.info(f'testing {self._condition}')
        logger.debug(f'context: {self._context}')
        logger.debug(f'inputs: {inputs}')
        return dry_run or self._test_fun(self, inputs=inputs)

    def _test_executable(self, inputs=[]):
        res = self._condition.execute(context=self._context, inputs=inputs)
        return res.return_code == 0

    def _no_input(self, inputs=[]):
        return not self._has_input(inputs=inputs)

    def _has_input(self, inputs=[]):
        return len(inputs) > 0


_PATTERNS = {
    Condition.NO_INPUT: Condition._no_input,
    Condition.HAS_INPUT: Condition._has_input,
}


def assert_condition(condition):
    if isinstance(condition, Executable):
        return condition, Condition._test_executable

    if isinstance(condition, str):
        test_fun = _PATTERNS.get(condition)
        if not test_fun:
            raise ValueError(f'{condition} is not defined')
        return condition, test_fun

    raise ValueError(f'unknow condition type: {type(condition)} ({condition})')
