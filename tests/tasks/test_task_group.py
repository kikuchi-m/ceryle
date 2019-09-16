import pytest

from ceryle import Command, Task, TaskGroup


def test_new_task_group():
    t1 = Task(Command('do some'), 'context')
    t2 = Task(Command('do awwsome'), 'context')
    tg = TaskGroup('new_task', [t1, t2])

    assert tg.name == 'new_task'
    assert tg.tasks == [t1, t2]


def test_new_task_group_deps():
    tg = TaskGroup('build', [], dependencies=['setup', 'pre-build'])
    assert tg.dependencies == ['setup', 'pre-build']
