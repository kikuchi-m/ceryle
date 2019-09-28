import abc
import logging

import ceryle.util as util
from ceryle.dsl.support import eval_arg

logger = logging.getLogger(__name__)


class Executable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self, *args, context=None, **kwargs):
        pass

    def preprocess(self, args, kwargs):
        processed_args = [eval_arg(v, fail_on_unknown=False) for v in args]
        processed_kwargs = dict([(k, eval_arg(v, fail_on_unknown=False)) for k, v in kwargs.items()])
        return processed_args, processed_kwargs


class ExecutionResult:
    def __init__(self, return_code, stdout=[], stderr=[]):
        self._return_code = return_code
        self._stdout = [util.assert_type(l, str) for l in stdout]
        self._stderr = [util.assert_type(l, str) for l in stderr]

    @property
    def return_code(self):
        return self._return_code

    @property
    def stdout(self):
        return [*self._stdout]

    @property
    def stderr(self):
        return [*self._stderr]

    def __str__(self):
        return f'{self.__class__.__name__}(return_code={self.return_code}, stdout={self.stdout}, stderr={self.stderr})'


class ExecutableWrapper(Executable):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = list(args)
        self._kwargs = dict(kwargs)
        logger.debug(f'ExecutableWrapper({func.__name__}, args={self._args}, kwargs={self._kwargs})')

    def execute(self, **kwargs):
        func_code = self._func.__code__
        extra_keys = func_code.co_varnames[len(self._args):func_code.co_argcount]
        kwdefaults = dict(zip(extra_keys, self._func.__defaults__ or ()))
        exact_kwargs = {}
        for k in [*self._kwargs.keys(), *kwdefaults.keys()]:
            exact_kwargs[k] = kwargs.get(k, self._kwargs.get(k, kwdefaults.get(k)))

        processed = self.preprocess(self._args, exact_kwargs)
        res = self._func(*processed[0], **processed[1])
        if res is None or isinstance(res, int):
            return ExecutionResult(res or 0)

        if not isinstance(res, ExecutionResult):
            raise RuntimeError(f'ExecutionResult was not returned by {self._func.__name__}')
        return res

    def __str__(self):
        args = ', '.join(self._args)
        kwargs = ', '.join(self._kwargs) if self._kwargs else ''
        return f'{self._func.__name__}({args}{kwargs})'


def executable(func):
    def wrapper(*args, **kwargs):
        logger.debug(f'ExecutableWrapper({func.__name__}, args={args}, kwargs={kwargs})')
        return ExecutableWrapper(func, *args, **kwargs)

    return wrapper
