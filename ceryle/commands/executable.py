import abc


class Executable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self, *args, context=None, **kwargs):
        pass


class ExecutionResult:
    def __init__(self, return_code):
        self._return_code = return_code

    @property
    def return_code(self):
        return self._return_code


class ExecutableWrapper(Executable):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = list(args)
        self._kwargs = dict(kwargs)

    def execute(self, **kwargs):
        func_code = self._func.__code__
        extra_keys = func_code.co_varnames[len(self._args):func_code.co_argcount]
        kwdefaults = dict(zip(extra_keys, self._func.__defaults__ or ()))
        exact_kwargs = {}
        for k in [*self._kwargs.keys(), *kwdefaults.keys()]:
            exact_kwargs[k] = kwargs.get(k, self._kwargs.get(k, kwdefaults.get(k)))

        res = self._func(*self._args, **exact_kwargs)
        if res is None or isinstance(res, int):
            return ExecutionResult(res or 0)

        if not isinstance(res, ExecutionResult):
            raise RuntimeError(f'ExecutionResult was not returned by {self._func.__name__}')
        return res


def executable(func):
    def wrapper(*args, **kwargs):
        return ExecutableWrapper(func, *args, **kwargs)

    return wrapper
