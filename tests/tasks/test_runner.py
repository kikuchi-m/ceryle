import pytest

from ceryle import Command, Task, TaskGroup, TaskRunner
from ceryle import TaskDependencyError


def test_new_task_runner():
    g1_tasks = [Task(Command('do a'))]
    g1 = TaskGroup('g1', g1_tasks, dependencies=['g2'])

    g2_tasks = [Task(Command('do b'))]
    g2 = TaskGroup('g2', g2_tasks, dependencies=[])

    TaskRunner([g1, g2])


def test_raises_dependency_error():
    g1_tasks = [Task(Command('do a'))]
    g1 = TaskGroup('g1', g1_tasks, dependencies=['g2'])

    g2_tasks = [Task(Command('do b'))]
    g2 = TaskGroup('g2', g2_tasks, dependencies=['g3'])

    # no depending task 'g3'
    with pytest.raises(TaskDependencyError):
        TaskRunner([g1, g2])

    g3_tasks = [Task(Command('do a'))]
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

    expected_calls = [mocker.call.g2_run(), mocker.call.g1_run()]

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g1') is True
    g1.run.assert_called_once_with()
    g2.run.assert_called_once_with()
    g3.run.assert_not_called()
    assert mock.mock_calls == expected_calls


def test_run_tasks_fails(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], dependencies=['g2'])
    g2 = TaskGroup('g2', [], dependencies=[])

    g1_run = mocker.patch.object(g1, 'run', return_value=True)
    mock.attach_mock(g1_run, 'g1_run')

    g2_run = mocker.patch.object(g2, 'run', return_value=False)
    mock.attach_mock(g2_run, 'g2_run')

    expected_calls = [mocker.call.g2_run()]

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is False
    g1.run.assert_not_called()
    g2.run.assert_called_once_with()
    assert mock.mock_calls == expected_calls
