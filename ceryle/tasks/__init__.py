from ceryle import CeryleException


class TaskDependencyError(CeryleException):
    pass


class TaskDefinitionError(CeryleException):
    pass


class TaskIOError(CeryleException):
    pass
