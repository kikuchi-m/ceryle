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


def test_raise_if_unacceptable_args():
    with pytest.raises(TypeError):
        Task(None, 'context')

    with pytest.raises(TypeError):
        Task('not an executable', 'context')

    with pytest.raises(TypeError):
        Task(Command('do some', None))

    with pytest.raises(TypeError):
        Task(Command('do some', 1))


def test_run_all_tasks(mocker):
    t1 = Task(Command('do some'), 'context')
    mocker.patch.object(t1, 'run', return_value=True)

    t2 = Task(Command('do awwsome'), 'context')
    mocker.patch.object(t2, 'run', return_value=True)

    tg = TaskGroup('new_task', [t1, t2])

    assert tg.run() is True
    t1.run.assert_called_once_with()
    t2.run.assert_called_once_with()


def test_run_fails_some_task(mocker):
    t1 = Task(Command('do some'), 'context')
    mocker.patch.object(t1, 'run', return_value=False)

    t2 = Task(Command('do awwsome'), 'context')
    mocker.patch.object(t2, 'run', return_value=True)

    tg = TaskGroup('new_task', [t1, t2])

    assert tg.run() is False
    t1.run.assert_called_once_with()
    t2.run.assert_not_called()
