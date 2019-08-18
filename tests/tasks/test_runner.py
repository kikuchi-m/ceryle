import pytest

from ceryle import Command, Task, TaskGroup, TaskRunner
from ceryle import TaskDependencyError, TaskDefinitionError


def test_new_task_runner():
    g1_tasks = [Task(Command('do a'), 'context')]
    g1 = TaskGroup('g1', g1_tasks, dependencies=['g2'])

    g2_tasks = [Task(Command('do b'), 'context')]
    g2 = TaskGroup('g2', g2_tasks, dependencies=[])

    TaskRunner([g1, g2])


def test_raises_dependency_error():
    g1_tasks = [Task(Command('do a'), 'context')]
    g1 = TaskGroup('g1', g1_tasks, dependencies=['g2'])

    g2_tasks = [Task(Command('do b'), 'context')]
    g2 = TaskGroup('g2', g2_tasks, dependencies=['g3'])

    # no depending task 'g3'
    with pytest.raises(TaskDependencyError):
        TaskRunner([g1, g2])

    g3_tasks = [Task(Command('do a'), 'context')]
    g3 = TaskGroup('g3', g3_tasks, dependencies=['g1'])

    # cyclic
    with pytest.raises(TaskDependencyError):
        TaskRunner([g1, g2, g3])


def test_run_tasks(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], dependencies=['g2'])
    g2 = TaskGroup('g2', [], dependencies=[])
    g3 = TaskGroup('g3', [], dependencies=[])

    g1_run = mocker.patch.object(g1, 'run', return_value=True)
    mock.attach_mock(g1_run, 'g1_run')

    g2_run = mocker.patch.object(g2, 'run', return_value=True)
    mock.attach_mock(g2_run, 'g2_run')

    g3_run = mocker.patch.object(g3, 'run')
    mock.attach_mock(g3_run, 'g3_run')

    expected_calls = [mocker.call.g2_run(dry_run=False), mocker.call.g1_run(dry_run=False)]

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g1') is True
    g1.run.assert_called_once_with(dry_run=False)
    g2.run.assert_called_once_with(dry_run=False)
    g3.run.assert_not_called()
    assert mock.mock_calls == expected_calls


def test_run_raises_task_not_defined():
    g1 = TaskGroup('g1', [], dependencies=['g2'])
    g2 = TaskGroup('g2', [], dependencies=[])

    runner = TaskRunner([g1, g2])

    with pytest.raises(TaskDefinitionError) as e:
        runner.run('g3')
    assert str(e.value) == 'task g3 is not defined'


def test_run_tasks_fails(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], dependencies=['g2'])
    g2 = TaskGroup('g2', [], dependencies=[])

    g1_run = mocker.patch.object(g1, 'run', return_value=True)
    mock.attach_mock(g1_run, 'g1_run')

    g2_run = mocker.patch.object(g2, 'run', return_value=False)
    mock.attach_mock(g2_run, 'g2_run')

    expected_calls = [mocker.call.g2_run(dry_run=False)]

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is False
    g1.run.assert_not_called()
    g2.run.assert_called_once_with(dry_run=False)
    assert mock.mock_calls == expected_calls


def test_dry_run(mocker):
    g1 = TaskGroup('g1', [], dependencies=['g2'])
    mocker.patch.object(g1, 'run', return_value=True)
    g2 = TaskGroup('g2', [], dependencies=[])
    mocker.patch.object(g2, 'run', return_value=True)

    runner = TaskRunner([g1, g2])

    assert runner.run('g1', dry_run=True) is True
    g1.run.assert_called_once_with(dry_run=True)
    g2.run.assert_called_once_with(dry_run=True)
