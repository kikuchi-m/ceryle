import abc
import ast
import os
import pathlib
import sys

import ceryle
import ceryle.util as util

from ceryle.commands.command import Command
from ceryle.commands.copy import Copy
from ceryle.commands.remove import Remove
from ceryle.commands.executable import executable, executable_with
from ceryle.commands.builtin import mkdir, save_input_to
from ceryle.tasks.task import SingleValueCommandInput
from ceryle.tasks.condition import Condition
from ceryle.dsl.parser import parse_tasks
from . import support, TaskFileError


if sys.version_info[0] < 3:
    raise RuntimeError(f'python {sys.version_info[0]}.{sys.version_info[1]} is not supported')
if sys.version_info[1] < 8:
    def ast_module(body):
        return ast.Module(body)
else:
    def ast_module(body):
        return ast.Module(body, [])


class FileLoaderBase(abc.ABC):
    def __init__(self, file):
        self._file = util.assert_type(file, str, pathlib.Path)

    def _evaluate_file(self, body, gvars, lvars):
        co = compile(ast_module(body), str(self._file), 'exec')
        exec(co, gvars, lvars)

    @abc.abstractmethod
    def load(self, global_vars={}, local_vars={}, additional_args={}):
        pass


class TaskFileLoader(FileLoaderBase):
    def __init__(self, file, root_context):
        super().__init__(file)
        self._root_context = pathlib.Path(util.assert_type(root_context, str, pathlib.Path))

    def load(self, global_vars={}, local_vars={}, additional_args={}):
        module = util.parse_to_ast(self._file)

        body = module.body
        if len(body) == 0:
            raise TaskFileError(f'No task definition found: {self._file}')

        gvars, lvars = _prepare_vars(global_vars, local_vars, additional_args)
        task_node = body[-1]
        if not isinstance(task_node, ast.Expr) or not isinstance(task_node.value, ast.Dict):
            raise TaskFileError(f'Not task definition, declare by dict form: {self._file}')

        self._evaluate_file(body[:-1], gvars, lvars)
        tasks = eval(compile(ast.Expression(task_node.value), self._file, 'eval'), gvars, lvars)
        context = self._resolve_context(lvars.get('context'))
        return TaskDefinition(parse_tasks(tasks, str(context), self._file), lvars.get('default'))

    def _resolve_context(self, context):
        if not context:
            return self._root_context
        if os.path.isabs(context):
            return context
        return self._root_context.joinpath(context)


class ExtensionLoader(FileLoaderBase):
    def __init__(self, file):
        super().__init__(file)

    def load(self, global_vars={}, local_vars={}, additional_args={}):
        module = util.parse_to_ast(self._file)
        gvars, lvars = _prepare_vars(global_vars, local_vars, additional_args)
        self._evaluate_file(module.body, gvars, lvars)
        return lvars


def _prepare_vars(global_vars, local_vars, additional_args):
    def arg_fun(name, **kwargs):
        return support.Arg(name, additional_args, **kwargs)

    gvars = global_vars.copy()
    gvars.update(
        ceryle=ceryle,
        command=Command,
        copy=Copy,
        remove=Remove,
        save_input_to=save_input_to,
        mkdir=mkdir,
        executable=executable,
        executable_with=executable_with,
        condition=Condition,
        path=support.joinpath,
        env=support.Env,
        arg=arg_fun,
        as_single_value=SingleValueCommandInput,
    )
    gvars.update(**local_vars)
    return gvars, local_vars.copy()


class TaskDefinition:
    def __init__(self, tasks, default_task=None):
        self._tasks = tasks.copy()
        self._default = default_task

    @property
    def tasks(self):
        return self._tasks.copy()

    @property
    def default_task(self):
        return self._default

    def find_task_group(self, name):
        util.assert_type(name, str)
        for g in self._tasks:
            if g.name == name:
                return g
        return None
