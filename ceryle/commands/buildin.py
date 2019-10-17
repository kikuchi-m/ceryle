import logging

import ceryle.util as util
from ceryle import executable, executable_with
from ceryle import Executable, TaskDefinitionError

logger = logging.getLogger(__name__)


@executable
def expression(code):
    logger.debug(f'evaluating [{code}]')
    res = eval(compile(code, '<expression>', 'eval'))
    if not isinstance(res, bool):
        raise TaskDefinitionError(f'return boolean value by expression: [{code}]')
    return res


@executable
def no_input(inputs=[]):
    return len(inputs) == 0


@executable
def has_input(inputs=[]):
    return len(inputs) > 0


def assert_executables(*executables):
    if len(executables) == 0:
        raise ValueError('one or more executables are required')
    for exe in executables:
        util.assert_type(exe, Executable)


@executable_with(assertion=assert_executables)
def execute_all(*executables, context=None, inputs=None):
    res = None
    for exe in executables:
        res = exe.execute(context=context, inputs=inputs)
        if res.return_code != 0:
            return res
    return res


@executable_with(assertion=assert_executables)
def execute_any(*executables, context=None, inputs=None):
    res = None
    for exe in executables:
        res = exe.execute(context=context, inputs=inputs)
        if res.return_code == 0:
            return res
    return res
