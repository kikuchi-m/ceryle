import abc


class Executable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass


class ExecutionResult:
    def __init__(self, return_code):
        self._return_code = return_code

    @property
    def return_code(self):
        return self._return_code
