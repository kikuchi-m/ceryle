import pytest

from ceryle import Command, Task, TaskGroup, TaskRunner, RunCache
from ceryle import TaskDependencyError, TaskDefinitionError, TaskIOError, IllegalOperation


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

    g1_t1 = Task(Command('do some'), 'context')
    g1_t2 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1, g1_t2], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')
    g1_t2_run = mocker.patch.object(g1_t2, 'run', return_value=True)
    mock.attach_mock(g1_t2_run, 'g1_t2_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    g3_t1_run = mocker.patch.object(g3_t1, 'run')
    mock.attach_mock(g3_t1_run, 'g3_t1_run')

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g1') is True
    g2_t1.run.assert_called_once()
    g1_t2.run.assert_called_once()
    g1_t1.run.assert_called_once()
    g3_t1.run.assert_not_called()
    assert mock.mock_calls == [
        mocker.call.g2_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t2_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_get_run_cache_raises_before_runnin():
    g1 = TaskGroup('g1', [])
    runner = TaskRunner([g1])

    with pytest.raises(IllegalOperation) as e:
        runner.get_cache()
    assert str(e.value) == 'could not get cache before running'


def test_run_raises_task_not_defined():
    g1 = TaskGroup('g1', [], dependencies=['g2'])
    g2 = TaskGroup('g2', [], dependencies=[])

    runner = TaskRunner([g1, g2])

    with pytest.raises(TaskDefinitionError) as e:
        runner.run('g3')
    assert str(e.value) == 'task g3 is not defined'

    with pytest.raises(IllegalOperation) as e:
        runner.get_cache()


def test_run_tasks_fails(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])
    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=False)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is False
    g2_t1.run.assert_called_once()
    g1_t1.run.assert_not_called()
    assert mock.mock_calls == [mocker.call.g2_t1_run(dry_run=False, inputs=[])]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', False),
    ]
    assert cache.register == {}


def test_run_tasks_fails_by_exception(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])
    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', side_effect=Exception('test'))
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    runner = TaskRunner([g1, g2])

    with pytest.raises(Exception):
        runner.run('g1')
    g2_t1.run.assert_called_once()
    g1_t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g2_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert cache.register == {}


def test_dry_run(mocker):
    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])
    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    mocker.patch.object(g1_t1, 'run', return_value=True)
    mocker.patch.object(g2_t1, 'run', return_value=True)

    runner = TaskRunner([g1, g2])

    assert runner.run('g1', dry_run=True) is True
    g2_t1.run.assert_called_once_with(dry_run=True, inputs=[])
    g1_t1.run.assert_called_once_with(dry_run=True, inputs=[])

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', False),
        ('g1', False),
    ]
    assert cache.register == {}


def test_run_task_with_stdout(mocker):
    g1_t1 = Task(Command('do some'), 'context', input=('g2', 'EXEC_STDOUT'))
    mocker.patch.object(g1_t1, 'stdout', return_value=[])
    mocker.patch.object(g1_t1, 'stderr', return_value=[])
    mocker.patch.object(g1_t1, 'run', return_value=True)
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context', stdout='EXEC_STDOUT')
    mocker.patch.object(g2_t1, 'stdout', return_value=['foo', 'bar'])
    mocker.patch.object(g2_t1, 'stderr', return_value=[])
    mocker.patch.object(g2_t1, 'run', return_value=True)
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is True
    g2_t1.run.assert_called_once_with(dry_run=False, inputs=[])
    g2_t1.stdout.assert_called_once()
    g2_t1.stderr.assert_not_called()
    g1_t1.run.assert_called_once_with(dry_run=False, inputs=['foo', 'bar'])
    g1_t1.stdout.assert_not_called()
    g1_t1.stderr.assert_not_called()

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', True),
    ]
    assert cache.register == {
        'g2': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }


def test_run_task_with_stdout_from_same_group(mocker):
    g1_t1 = Task(Command('do some'), 'context', stdout='EXEC_STDOUT')
    mocker.patch.object(g1_t1, 'stdout', return_value=['foo', 'bar'])
    mocker.patch.object(g1_t1, 'stderr', return_value=[])
    mocker.patch.object(g1_t1, 'run', return_value=True)

    g1_t2 = Task(Command('do some'), 'context', input='EXEC_STDOUT')
    mocker.patch.object(g1_t2, 'stdout', return_value=[])
    mocker.patch.object(g1_t2, 'stderr', return_value=[])
    mocker.patch.object(g1_t2, 'run', return_value=True)

    g1 = TaskGroup('g1', [g1_t1, g1_t2], dependencies=[])

    runner = TaskRunner([g1])

    assert runner.run('g1') is True
    g1_t2.run.assert_called_once_with(dry_run=False, inputs=['foo', 'bar'])
    g1_t2.stdout.assert_not_called()
    g1_t2.stderr.assert_not_called()
    g1_t1.run.assert_called_once_with(dry_run=False, inputs=[])
    g1_t1.stdout.assert_called_once()
    g1_t1.stderr.assert_not_called()

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g1', True),
    ]
    assert cache.register == {
        'g1': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }


def test_run_task_with_stderr(mocker):
    g1_t1 = Task(Command('do some'), 'context', input=('g2', 'EXEC_STDERR'))
    mocker.patch.object(g1_t1, 'stdout', return_value=[])
    mocker.patch.object(g1_t1, 'stderr', return_value=[])
    mocker.patch.object(g1_t1, 'run', return_value=True)
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context', stderr='EXEC_STDERR')
    mocker.patch.object(g2_t1, 'stdout', return_value=[])
    mocker.patch.object(g2_t1, 'stderr', return_value=['foo', 'bar'])
    mocker.patch.object(g2_t1, 'run', return_value=True)
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is True
    g2_t1.run.assert_called_once_with(dry_run=False, inputs=[])
    g2_t1.stdout.assert_not_called()
    g2_t1.stderr.assert_called_once()
    g1_t1.run.assert_called_once_with(dry_run=False, inputs=['foo', 'bar'])
    g1_t1.stdout.assert_not_called()
    g1_t1.stderr.assert_not_called()

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', True),
    ]
    assert cache.register == {
        'g2': {
            'EXEC_STDERR': ['foo', 'bar'],
        },
    }


def test_run_failed_by_invalid_io(mocker):
    g1_t1 = Task(Command('do some'), 'context', input='EXEC_STDOUT')
    mocker.patch.object(g1_t1, 'run', return_value=True)
    g1 = TaskGroup('g1', [g1_t1], dependencies=[])

    runner = TaskRunner([g1])

    with pytest.raises(TaskIOError) as ex:
        runner.run('g1')
    g1_t1.run.assert_not_called()
    assert str(ex.value) == 'EXEC_STDOUT is required by a task in g1, but not registered'

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g1', False),
    ]
    assert cache.register == {}


def test_run_skip_task_already_run(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2', 'g3'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=['g4'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], dependencies=['g4'])

    g4_t1 = Task(Command('do some'), 'context')
    g4 = TaskGroup('g4', [g4_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    g3_t1_run = mocker.patch.object(g3_t1, 'run', return_value=True)
    mock.attach_mock(g3_t1_run, 'g3_t1_run')

    g4_t1_run = mocker.patch.object(g4_t1, 'run', return_value=True)
    mock.attach_mock(g4_t1_run, 'g4_t1_run')

    runner = TaskRunner([g1, g2, g3, g4])

    assert runner.run('g1') is True
    g4_t1.run.assert_called_once()
    g2_t1.run.assert_called_once()
    g3_t1.run.assert_called_once()
    g1_t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g4_t1_run(dry_run=False, inputs=[]),
        mocker.call.g2_t1_run(dry_run=False, inputs=[]),
        mocker.call.g3_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g4', True),
        ('g2', True),
        ('g3', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_run_skip_succeeded_tasks(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    last_run_cache = RunCache('g1')
    last_run_cache.add_result(('g2', True))
    last_run_cache.add_result(('g1', False))

    runner = TaskRunner([g1, g2])

    assert runner.run('g1', last_run=last_run_cache) is True
    g2_t1.run.assert_not_called()
    g1_t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_run_skip_succeeded_tasks_in_new_deps_tree(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g3'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g3_t1_run = mocker.patch.object(g3_t1, 'run', return_value=True)
    mock.attach_mock(g3_t1_run, 'g3_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    last_run_cache = RunCache('g1')
    last_run_cache.add_result(('g2', True))
    last_run_cache.add_result(('g1', True))

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g1', last_run=last_run_cache) is True
    g2_t1.run.assert_not_called()
    g3_t1.run.assert_called_once()
    g1_t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g3_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g3', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_run_all_since_last_is_differnt_task(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], dependencies=['g2'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], dependencies=[])

    g1_t1_run = mocker.patch.object(g1_t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')

    g3_t1_run = mocker.patch.object(g3_t1, 'run', return_value=True)
    mock.attach_mock(g3_t1_run, 'g3_t1_run')

    g2_t1_run = mocker.patch.object(g2_t1, 'run', return_value=True)
    mock.attach_mock(g2_t1_run, 'g2_t1_run')

    last_run_cache = RunCache('g1')
    last_run_cache.add_result(('g2', True))
    last_run_cache.add_result(('g1', False))

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g3', last_run=last_run_cache) is True
    g2_t1.run.assert_called_once()
    g3_t1.run.assert_called_once()
    g1_t1.run.assert_not_called
    assert mock.mock_calls == [
        mocker.call.g2_t1_run(dry_run=False, inputs=[]),
        mocker.call.g3_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g3'
    assert cache.results == [
        ('g2', True),
        ('g3', True),
    ]
    assert cache.register == {}
