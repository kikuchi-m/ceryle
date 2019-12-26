import logging
import os
import pathlib

import ceryle.util as util
from ceryle.commands.executable import executable, executable_with, Executable, ExecutionResult
from ceryle.tasks import TaskDefinitionError

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


def assert_exec_args(*executables):
    if len(executables) == 0:
        raise ValueError('one or more executables are required')
    for exe in executables:
        util.assert_type(exe, Executable, bool)


@executable_with(assertion=assert_exec_args, name='all')
def execute_all(*executables, context=None, inputs=None):
    for exe in executables:
        if isinstance(exe, bool):
            if exe:
                continue
            else:
                return ExecutionResult(1)
        res = exe.execute(context=context, inputs=inputs)
        if res.return_code != 0:
            return res
    return ExecutionResult(0)


@executable_with(assertion=assert_exec_args, name='any')
def execute_any(*executables, context=None, inputs=None):
    res = None
    for exe in executables:
        if isinstance(exe, bool):
            if exe:
                return ExecutionResult(0)
            else:
                continue
        res = exe.execute(context=context, inputs=inputs)
        if res.return_code == 0:
            return res
    return res or ExecutionResult(1)


def assert_xfail_arg(executable):
    util.assert_type(executable, Executable, bool)


@executable_with(assertion=assert_xfail_arg, name='fail')
def expect_fail(executable, context=None, inputs=None):
    if isinstance(executable, bool):
        return ExecutionResult(int(executable))
    res = executable.execute(context=context, inputs=inputs)
    return ExecutionResult(int(not bool(res.return_code)),
                           stdout=res.stdout,
                           stderr=res.stderr)


@executable
def save_input_to(path, overwrite=False, context=None, inputs=[]):
    p = pathlib.Path(context, path)
    if p.exists() and overwrite is False:
        util.print_err(f'file already exists: {p}')
        return ExecutionResult(1)

    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'wb') as fp:
        fp.write(os.linesep.join(inputs).encode())
    return ExecutionResult(0)
