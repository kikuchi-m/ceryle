import abc
import os
import pathlib

import ceryle.util as util
from ceryle import NoEnvironmentError


def joinpath(*path):
    return str(pathlib.Path(*path))


class ArgumentBase(abc.ABC):
    @abc.abstractmethod
    def evaluate(self):
        pass


class Env(ArgumentBase):
    def __init__(self, name, default=None, allow_empty=False):
        self._name = util.assert_type(name, str)
        self._default = util.assert_type(default, str, None)
        self._allow_empty = util.assert_type(allow_empty, bool)

    def evaluate(self):
        v = os.environ.get(self._name, self._default or '')
        if not self._allow_empty and v == '':
            raise NoEnvironmentError(f'environment variable {self._name} is not defined')
        return v
