import ceryle.util as util

from ceryle.commands.executable import Executable


class Task:
    def __init__(self, executable, context):
        util.assert_type(executable, Executable)
        util.assert_type(context, str)
        self._executable = executable
        self._context = context

    def run(self, dry_run=False):
        print(f'running {self._executable}')
        if dry_run:
            return True
        res = self._executable.execute(context=self._context)
        success = res.return_code == 0
        if not success:
            util.print_err(f'task failed: {repr(self._executable)}')
        return success

    @property
    def executable(self):
        return self._executable

    @property
    def context(self):
        return self._context


class TaskGroup:
    def __init__(self, name, tasks, dependencies=[]):
        self._name = name
        self._tasks = list(tasks)
        self._dependencies = list(dependencies)

    def run(self, dry_run=False):
        for t in self._tasks:
            if not t.run(dry_run=dry_run):
                return False
        return True

    @property
    def name(self):
        return self._name

    @property
    def tasks(self):
        return list(self._tasks)

    @property
    def dependencies(self):
        return list(self._dependencies)
