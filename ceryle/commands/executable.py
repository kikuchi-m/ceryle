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
        logger.debug(f'preprocessing args: [{args}], kwargs: {kwargs}')
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
    def __init__(self, func, args, kwargs, name=None):
        self._func = func
        self._args = args[:]
        self._kwargs = kwargs.copy()
        self._name = name

    def execute(self, **kwargs):
        exact_kwargs = self._exact_kwargs(kwargs)
        processed = self.preprocess(self._args, exact_kwargs)
        logger.debug(f'preprocessed executable: {self._func.__name__}, args: {processed[0]}, kwargs: {processed[1]}')
        res = self._func(*processed[0], **processed[1])
        if isinstance(res, bool):
            return ExecutionResult(int(not res))

        if res is None or isinstance(res, int):
            return ExecutionResult(res or 0)

        if not isinstance(res, ExecutionResult):
            raise RuntimeError(f'ExecutionResult was not returned by {self._func.__name__}')
        return res

    def _exact_kwargs(self, kwargs):
        defaults = self._func.__defaults__
        flags = self._func.__code__.co_flags
        varnames = self._func.__code__.co_varnames
        ac = self._func.__code__.co_argcount
        kwoac = self._func.__code__.co_kwonlyargcount

        if flags & 0x04 and not defaults:
            extra_keys = varnames[ac:ac + kwoac]
        elif not defaults:
            extra_keys = []
        else:
            extra_keys = varnames[ac - len(defaults):ac]

        defined_kwargs = self._kwargs.copy()
        runtime_kwargs = kwargs.copy()
        kwdefaults = {}
        logger.debug(f'determining kwargs for {self._func.__name__}')
        logger.debug(f'defined kwargs: {defined_kwargs}')
        logger.debug(f'runtime kwargs: {runtime_kwargs}')

        if kwoac:
            exact_keys = (set(runtime_kwargs.keys()) | set(defined_kwargs.keys())) & set(extra_keys)
        else:
            if defaults:
                kwdefaults = dict(zip(extra_keys, defaults))
            exact_keys = (set(defined_kwargs.keys()) & set(extra_keys)) | set(kwdefaults.keys())

        exact_kwargs = dict([
            (k, runtime_kwargs.pop(k, defined_kwargs.pop(k, kwdefaults.get(k))))
            for k in exact_keys])

        if flags & 0x08:
            exact_kwargs.update(**defined_kwargs)
            exact_kwargs.update(**runtime_kwargs)

        logger.debug(f'precice kwargs for {self._func.__name__}: {exact_kwargs}')
        return exact_kwargs

    def __str__(self):
        args = ', '.join([str(a) for a in self._args])
        kwargs = ', '.join([f'{k}={v}' for k, v in self._kwargs.items()])
        if kwargs:
            kwargs = f', {kwargs}'
        return f'{self._name or self._func.__name__}({args}{kwargs})'


def executable(func, assertion=None, name=None):
    def wrapper(*args, **kwargs):
        logger.debug(f'ExecutableWrapper({func.__name__}, args={args}, kwargs={kwargs})')
        if assertion:
            logger.debug(f'assert arguments by {assertion.__name__}')
            assertion(*args, **kwargs)
        return ExecutableWrapper(func, args, kwargs, name=name)

    return wrapper


def executable_with(assertion=None, name=None):
    def wrapper(func):
        return executable(func, assertion=assertion, name=name)

    return wrapper
