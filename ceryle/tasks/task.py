from ceryle.util import print_err


class Task:
    def __init__(self, executable):
        self._executable = executable

    def run(self):
        rc = self._executable.execute()
        success = rc is 0
        if not success:
            print_err(f'task failed: {repr(self._executable)}')
        return success
