from ceryle import CeryleException


class TaskFileError(CeryleException):
    pass


class NoEnvironmentError(CeryleException):
    pass


class NoArgumentError(CeryleException):
    pass
