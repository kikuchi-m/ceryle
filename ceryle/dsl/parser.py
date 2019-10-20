import ceryle.util as util

from . import TaskFileError
from ceryle.commands.executable import Executable
from ceryle.tasks.task import Task, TaskGroup

TASKS = 'tasks'
RUN = 'run'


def parse_tasks(raw_tasks, context, filename):
    util.assert_type(raw_tasks, dict)
    util.assert_type(context, str)

    tasks = []
    for gn, raw_group in raw_tasks.items():
        if isinstance(raw_group, list):
            g_tasks = [_to_task(t, context, gn) for t in raw_group]
            tasks.append(TaskGroup(gn, g_tasks, filename))
        else:
            if TASKS not in raw_group:
                g_tasks = []
            else:
                g_tasks = [_to_task(t, context, gn) for t in raw_group.pop(TASKS)]
            tasks.append(TaskGroup(gn, g_tasks, filename, **raw_group))
    return tasks


def _to_task(raw_task, context, group):
    if isinstance(raw_task, Executable):
        return Task(raw_task, context=context)
    if RUN not in raw_task:
        raise TaskFileError(f'{RUN}` is not declared in a task of {group}')
    return Task(raw_task.pop(RUN), context=context, **raw_task)
