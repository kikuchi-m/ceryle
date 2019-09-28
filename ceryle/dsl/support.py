import abc
import os
import pathlib

import ceryle.util as util
from . import NoArgumentError, NoEnvironmentError


def joinpath(*path):
    return str(pathlib.Path(*path))


class ArgumentBase(abc.ABC):
    def __init__(self):
        self._right = None
        self._left = None

    @abc.abstractmethod
    def evaluate(self):
        pass

    def __add__(self, o):
        return self._join(o)

    def __radd__(self, o):
        return self._join(o, left=True)

    def _join(self, o, left=False):
        util.assert_type(o, str, ArgumentBase)
        ne = self._copy()
        if left:
            ne._left = o
        else:
            ne._right = o
        return ne

    @abc.abstractmethod
    def _copy(self):
        pass

    def _eval_all(self, v):
        r = (self._right and _eval(self._right)) or ''
        l = (self._left and _eval(self._left)) or ''
        return f'{l}{v}{r}'


def _eval(a):
    if isinstance(a, str):
        return a
    if isinstance(a, ArgumentBase):
        return a.evaluate()
    raise ValueError(f'not a str or ArgumentBase: {a}')


class Env(ArgumentBase):
    def __init__(self, name, default=None, allow_empty=False):
        super().__init__()
        self._name = util.assert_type(name, str)
        self._default = util.assert_type(default, str, None)
        self._allow_empty = util.assert_type(allow_empty, bool)

    def evaluate(self):
        v = os.environ.get(self._name, self._default or '')
        if not self._allow_empty and v == '':
            raise NoEnvironmentError(f'environment variable {self._name} is not defined')
        return self._eval_all(v)

    def _copy(self):
        return Env(self._name, default=self._default, allow_empty=self._allow_empty)


class Arg(ArgumentBase):
    def __init__(self, name, args, default=None, allow_empty=False):
        super().__init__()
        self._name = util.assert_type(name, str)
        self._args = dict(**args)
        for k, v in self._args.items():
            util.assert_type(k, str)
            util.assert_type(v, str)
        self._default = util.assert_type(default, str, None)
        self._allow_empty = util.assert_type(allow_empty, bool)

    def evaluate(self):
        v = self._args.get(self._name, self._default or '')
        if not self._allow_empty and v == '':
            raise NoArgumentError(f'argument {self._name} is not defined')
        return self._eval_all(v)

    def _copy(self):
        return Arg(self._name, self._args, default=self._default, allow_empty=self._allow_empty)
