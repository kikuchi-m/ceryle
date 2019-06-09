import ceryle.util as util

from ceryle.commands.executable import Executable


class Task:
    def __init__(self, executable):
        util.assert_type(executable, Executable)
        self._executable = executable

    def run(self):
        rc = self._executable.execute()
        success = rc == 0
        if not success:
            util.print_err(f'task failed: {repr(self._executable)}')
        return success

    @property
    def executable(self):
        return self._executable


class TaskGroup:
    def __init__(self, name, tasks, dependencies=[]):
        self._name = name
        self._tasks = list(tasks)
        self._dependencies = list(dependencies)

    def run(self):
        for t in self._tasks:
            if not t.run():
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
