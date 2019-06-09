import ast
import ceryle.util as util
import collections
import os

from . import TaskFileError
from ceryle.commands.command import Command
from ceryle.dsl.parser import parse_tasks


class TaskFileLoader:
    def __init__(self, task_file):
        self._task_file = task_file

    def load(self):
        module = util.parse_to_ast(self._task_file)

        body = module.body
        if not body:
            raise TaskFileError(f'no task definition in {self._task_file}')

        task_node = body[-1]
        if not isinstance(task_node, ast.Expr) or not isinstance(task_node.value, ast.Dict):
            raise TaskFileError(f'task definition must be dict; file {self._task_file}')

        gvars = dict()
        lvars = dict(command=Command)

        if len(body) > 1:
            co = compile(ast.Module(body[:-1]), self._task_file, 'exec')
            exec(co, gvars, lvars)

        tasks = eval(compile(ast.Expression(task_node.value), self._task_file, 'eval'), gvars, lvars)
        return TaskDefinition(
            parse_tasks(tasks),
            self._resolve_context(lvars.get('context')),
            lvars.get('default'))

    def _resolve_context(self, context):
        if not context:
            return os.path.dirname(os.path.abspath(self._task_file))
        if os.path.isabs(context):
            return context
        return os.path.abspath(os.path.join(os.path.dirname(self._task_file), context))


TaskDefinition = collections.namedtuple(
    'TaskDefinition',
    ['tasks',
     'context',
     'default_task'])
