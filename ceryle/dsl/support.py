import abc
import logging
import os
import pathlib

import ceryle.util as util
from . import NoArgumentError, NoEnvironmentError

logger = logging.getLogger(__name__)


class ArgumentBase(abc.ABC):
    def __init__(self, name, default=None, allow_empty=False, format=None):
        self._name = util.assert_type(name, str)
        self._default = util.assert_type(default, str, None)
        self._allow_empty = util.assert_type(allow_empty, bool)
        self._format = util.assert_type(format, str, None)
        self._other = None
        self._left = False
        self._original = None


    def __add__(self, o):
        return self._join(o)

    def __radd__(self, o):
        return self._join(o, left=True)

    def _join(self, o, left=False):
        util.assert_type(o, str, ArgumentBase)
        a = self._copy()
        a._original = self
        a._other = o
        a._left = left
        return a

    @abc.abstractmethod
    def _copy(self):
        pass

    @abc.abstractmethod
    def _eval_var(self):
        pass

    def evaluate(self):
        logger.debug(f'evaluating {self}')
        v = self._original.evaluate() if self._original else self._eval_var()
        o = eval_arg(self._other) if self._other else ''
        return f'{o}{v}' if self._left else f'{v}{o}'

    def _format_value(self, v):
        return self._format and self._format % {self._name: v} or v

    def __str__(self):
        v = str(self._original) if self._original else self._str_format()
        if self._other:
            o = _str_format(self._other)
            return f'{o} + {v}' if self._left else f'{v} + {o}'
        return v

    @abc.abstractmethod
    def _str_format(self):
        pass

    def _str_args(self):
        ss = [self._name]
        if self._default is not None:
            ss.append(f'default={self._default}')
        if self._allow_empty:
            ss.append('allow_empty')
        if self._format:
            ss.append(f'format=\'{self._format}\'')
        return ss

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        if type(other) is not type(self):
            return NotImplemented
        return self.__dict__ == other.__dict__


def eval_arg(a, fail_on_unknown=True):
    if isinstance(a, str):
        return a
    if isinstance(a, ArgumentBase):
        return a.evaluate()
    if fail_on_unknown:
        raise ValueError(f'not a str or ArgumentBase: {a}')
    return a


def _str_format(a):
    util.assert_type(a, str, ArgumentBase)
    if isinstance(a, str):
        return f"'{a}'"
    if isinstance(a, ArgumentBase):
        return str(a)


class Env(ArgumentBase):
    def __init__(self, name, default=None, allow_empty=False, format=None):
        super().__init__(name, default=default, allow_empty=allow_empty, format=format)

    def _eval_var(self):
        v = os.environ.get(self._name) or self._default or ''
        if not self._allow_empty and v == '':
            raise NoEnvironmentError(f'environment variable {self._name} is not defined')
        return self._format_value(v)

    def _copy(self):
        return Env(self._name, default=self._default, allow_empty=self._allow_empty, format=self._format)

    def _str_format(self):
        args = ', '.join(self._str_args())
        return f'env({args})'


class Arg(ArgumentBase):
    def __init__(self, name, args, default=None, allow_empty=False, format=None):
        super().__init__(name, default=default, allow_empty=allow_empty, format=format)
        self._args = dict(**args)
        for k, v in self._args.items():
            util.assert_type(k, str)
            util.assert_type(v, str)

    def _eval_var(self):
        v = self._args.get(self._name) or os.environ.get(self._name) or self._default or ''
        if not self._allow_empty and v == '':
            raise NoArgumentError(f'argument {self._name} is not defined')
        return self._format_value(v)

    def _copy(self):
        return Arg(self._name, self._args, default=self._default, allow_empty=self._allow_empty, format=self._format)

    def _str_format(self):
        args = ', '.join(self._str_args())
        return f'arg({args})'


class PathArg(ArgumentBase):
    def __init__(self, *segments):
        super().__init__('PathArg')
        if len(segments) == 0:
            raise ValueError('require at least 1 segment')
        self._segments = [util.assert_type(seg, str, ArgumentBase) for seg in segments]

    def _copy(self):
        return PathArg(*self._segments)

    def _eval_var(self):
        return pathlib.Path(*[_eval_path_seg(s) for s in self._segments])

    def _str_format(self):
        p = '/'.join([str(s) for s in self._segments])
        return f'path({p})'


def _eval_path_seg(s):
    if isinstance(s, str):
        return s
    if isinstance(s, ArgumentBase):
        return s.evaluate()
    raise TypeError(f'could not evaluate {type(s)} ({s})')


def joinpath(*path):
    return PathArg(*path)
