import logging
import pathlib

import ceryle
import ceryle.util as util

from ceryle.commands.executable import Executable, ExecutionResult
from ceryle.tasks import TaskIOError
from ceryle.tasks.condition import Condition

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, executable,
                 stdout=None, stderr=None, input=None,
                 ignore_failure=False, conditional_on=None):
        self._executable = util.assert_type(executable, Executable)
        self._stdout = util.assert_type(stdout, None, str)
        self._stderr = util.assert_type(stderr, None, str)
        self._input = util.assert_type(input, None, str, tuple, list)
        if self._input and not isinstance(self._input, str):
            if len([util.assert_type(k, str) for k in self._input]) != 2:
                raise ValueError('input key must be str or str list with length 2')
        self._ignore_failure = util.assert_type(ignore_failure, bool)
        self._condition = None if conditional_on is None else Condition(conditional_on)
        self._res = None

    def run(self, context, dry_run=False, inputs=[]):
        msg = f'running {self._executable}'
        iomsg = ', '.join([f'{io[0]}={io[1]}'
                           for io in [('input', self._input), ('stdout', self._stdout), ('stderr', self._stderr)]
                           if io[1]])
        if iomsg:
            msg = f'{msg} ({iomsg})'
        util.print_out(msg)
        if self._condition and not self._condition.test(context=context, dry_run=dry_run, inputs=inputs):
            util.print_out('skipping task since condition did not match')
            self._res = ExecutionResult(0)
            return True
        if dry_run:
            self._res = ExecutionResult(0)
            return True
        logger.debug(f'context={context}')
        logger.debug(f'inputs={inputs}')
        self._res = self._executable.execute(context=context, inputs=inputs)
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
    def __init__(self, name, tasks, context, filename,
                 dependencies=[], allow_skip=True):
        self._name = util.assert_type(name, str)
        self._tasks = [util.assert_type(t, Task) for t in util.assert_type(tasks, list)]
        self._context = util.assert_type(context, str, pathlib.Path)
        self._dependencies = [util.assert_type(d, str) for d in util.assert_type(dependencies, list)]
        self._filename = util.assert_type(filename, str, pathlib.Path)
        self._allow_skip = util.assert_type(allow_skip, bool)

    @property
    def name(self):
        return self._name

    @property
    def tasks(self):
        return list(self._tasks)

    @property
    def context(self):
        return self._context

    @property
    def dependencies(self):
        return list(self._dependencies)

    @property
    def allow_skip(self):
        return self._allow_skip

    @property
    def filename(self):
        return self._filename

    def run(self, dry_run=False, register={}):
        r = copy_register(register)
        for t in self.tasks:
            inputs = []
            if t.input_key:
                if isinstance(t.input_key, str):
                    logger.debug(f'read {self.name}.{t.input_key} from register')
                    inputs = util.getin(r, self.name, t.input_key)
                else:
                    logger.debug(f'read {".".join(t.input_key)} from register')
                    inputs = util.getin(r, *t.input_key)
                if inputs is None:
                    raise TaskIOError(f'{t.input_key} is required by a task in {self.name}, but not registered')
            if not t.run(self._context, dry_run=dry_run, inputs=inputs):
                return False, r
            if t.stdout_key:
                logger.debug(f'register {t.stdout_key}')
                _update_register(r, self.name, t.stdout_key, t.stdout())
            if t.stderr_key:
                logger.debug(f'register {t.stderr_key}')
                _update_register(r, self.name, t.stderr_key, t.stderr())
        return True, r


def _update_register(register, group, key, std):
    tg_r = util.getin(register, group, default={})
    tg_r.update({key: std})
    register.update({group: tg_r})


def copy_register(register):
    return dict([(g, register[g].copy()) for g in register])
