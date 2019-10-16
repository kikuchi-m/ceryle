import logging

from ceryle import executable, TaskDefinitionError

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
