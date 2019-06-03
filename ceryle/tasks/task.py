from ceryle import Executable
from ceryle.util import assert_type, print_err


class Task:
    def __init__(self, executable):
        assert_type(executable, Executable)
        self._executable = executable

    def run(self):
        rc = self._executable.execute()
        success = rc is 0
        if not success:
            print_err(f'task failed: {repr(self._executable)}')
        return success


class TaskGroup:
    def __init__(self, name, tasks):
        self._name = name
        self._tasks = list(tasks)

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
