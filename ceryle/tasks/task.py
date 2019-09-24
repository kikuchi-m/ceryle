import logging

import ceryle
import ceryle.util as util

from ceryle.commands.executable import Executable, ExecutionResult

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, executable, context,
                 stdout=None, stderr=None, input=None):
        self._executable = util.assert_type(executable, Executable)
        self._context = util.assert_type(context, str)
        self._stdout = util.assert_type(stdout, None, str)
        self._stderr = util.assert_type(stderr, None, str)
        self._input = util.assert_type(input, None, str)
        self._res = None

    def run(self, dry_run=False, inputs=[]):
        util.print_out(f'running {self._executable}')
        if dry_run:
            self._res = ExecutionResult(0)
            return True
        logger.debug(f'context={self._context}')
        logger.debug(f'inputs={inputs}')
        self._res = self._executable.execute(context=self._context, inputs=inputs)
        success = self._res.return_code == 0
        if not success:
            util.print_err(f'task failed: {self._executable}')
        return success

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
