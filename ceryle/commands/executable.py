import abc


class Executable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass
