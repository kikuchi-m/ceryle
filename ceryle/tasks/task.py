import logging

import ceryle
import ceryle.util as util

from ceryle.commands.executable import Executable, ExecutionResult
from ceryle.tasks.condition import Condition

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, executable, context,
                 stdout=None, stderr=None, input=None,
                 ignore_failure=False, conditional_on=None):
        self._executable = util.assert_type(executable, Executable)
        self._context = util.assert_type(context, str)
        self._stdout = util.assert_type(stdout, None, str)
        self._stderr = util.assert_type(stderr, None, str)
        self._input = util.assert_type(input, None, str, tuple, list)
        if self._input and not isinstance(self._input, str):
            if len([util.assert_type(k, str) for k in self._input]) != 2:
                raise ValueError('input key must be str or str list with length 2')
        self._ignore_failure = util.assert_type(ignore_failure, bool)
        self._condition = conditional_on and Condition(conditional_on, context)
        self._res = None

    def run(self, dry_run=False, inputs=[]):
        msg = f'running {self._executable}'
        iomsg = ', '.join([f'{io[0]}={io[1]}'
                           for io in [('input', self._input), ('stdout', self._stdout), ('stderr', self._stderr)]
                           if io[1]])
        if iomsg:
            msg = f'{msg} ({iomsg})'
        util.print_out(msg)
        if self._condition and not self._condition.test(dry_run=dry_run, inputs=inputs):
            util.print_out('skipping task since condition did not match')
            self._res = ExecutionResult(0)
            return True
        if dry_run:
            self._res = ExecutionResult(0)
            return True
        logger.debug(f'context={self._context}')
        logger.debug(f'inputs={inputs}')
        self._res = self._executable.execute(context=self._context, inputs=inputs)
        success = self._res.return_code == 0
        if not success:
            msg = f'task failed: {self._executable}'
            if self._ignore_failure:
                msg = f'{msg}, but ignore'
            util.print_err(msg)
        return self._ignore_failure or success

    @property
    def executable(self):
        return self._executable

    @property
    def context(self):
        return self._context

    @property
    def stdout_key(self):
        return self._stdout

    @property
    def stderr_key(self):
        return self._stderr

    @property
    def input_key(self):
        return self._input

    def stdout(self):
        if self._res is None:
            raise ceryle.IllegalOperation('task is not run yet')
        return self._res.stdout

    def stderr(self):
        if self._res is None:
            raise ceryle.IllegalOperation('task is not run yet')
        return self._res.stderr


class TaskGroup:
    def __init__(self, name, tasks, dependencies=[]):
        self._name = util.assert_type(name, str)
        self._tasks = [util.assert_type(t, Task) for t in util.assert_type(tasks, list)]
        self._dependencies = [util.assert_type(d, str) for d in util.assert_type(dependencies, list)]

    @property
    def name(self):
        return self._name

    @property
    def tasks(self):
        return list(self._tasks)

    @property
    def dependencies(self):
        return list(self._dependencies)
