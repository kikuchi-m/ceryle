import pytest

import ceryle.util as util
from ceryle import Command, Task, TaskGroup, TaskRunner, RunCache
from ceryle import TaskDependencyError, TaskDefinitionError, IllegalOperation


def test_new_task_runner():
    g1_tasks = [Task(Command('do a'), 'context')]
    g1 = TaskGroup('g1', g1_tasks, 'file1.ceryle', dependencies=['g2'])

    g2_tasks = [Task(Command('do b'), 'context')]
    g2 = TaskGroup('g2', g2_tasks, 'file1.ceryle', dependencies=[])

    TaskRunner([g1, g2])


def test_raises_dependency_error():
    g1_tasks = [Task(Command('do a'), 'context')]
    g1 = TaskGroup('g1', g1_tasks, 'file1.ceryle', dependencies=['g2'])

    g2_tasks = [Task(Command('do b'), 'context')]
    g2 = TaskGroup('g2', g2_tasks, 'file1.ceryle', dependencies=['g3'])

    # no depending task 'g3'
    with pytest.raises(TaskDependencyError):
        TaskRunner([g1, g2])

    g3_tasks = [Task(Command('do a'), 'context')]
    g3 = TaskGroup('g3', g3_tasks, 'file1.ceryle', dependencies=['g1'])

    # cyclic
    with pytest.raises(TaskDependencyError):
        TaskRunner([g1, g2, g3])


def test_run_tasks(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    g1_run = mocker.patch.object(g1, 'run', return_value=(True, {}))
    mock.attach_mock(g1_run, 'g1_run')

    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])
    g2_run = mocker.patch.object(g2, 'run', return_value=(True, {}))
    mock.attach_mock(g2_run, 'g2_run')

    g3 = TaskGroup('g3', [], 'file1.ceryle', dependencies=[])
    g3_run = mocker.patch.object(g3, 'run', return_value=(True, {}))
    mock.attach_mock(g3_run, 'g3_run')

    runner = TaskRunner([g1, g2, g3])

    assert runner.run('g1') is True
    g2.run.assert_called_once()
    g1.run.assert_called_once()
    g3.run.assert_not_called()
    assert mock.mock_calls == [
        mocker.call.g2_run(dry_run=False, register={}),
        mocker.call.g1_run(dry_run=False, register={}),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_get_run_cache_raises_before_runnin():
    g1 = TaskGroup('g1', [], 'file1.ceryle')
    runner = TaskRunner([g1])

    with pytest.raises(IllegalOperation) as e:
        runner.get_cache()
    assert str(e.value) == 'could not get cache before running'


def test_run_raises_task_not_defined():
    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])

    runner = TaskRunner([g1, g2])

    with pytest.raises(TaskDefinitionError) as e:
        runner.run('g3')
    assert str(e.value) == 'task g3 is not defined'

    with pytest.raises(IllegalOperation) as e:
        runner.get_cache()


def test_run_task_not_defined_print_similar_tasks():
    g1 = TaskGroup('build-foo', [], 'file1.ceryle', dependencies=[])
    g2 = TaskGroup('build-bar', [], 'file1.ceryle', dependencies=[])
    g3 = TaskGroup('build-all', [], 'file1.ceryle', dependencies=[])
    g4 = TaskGroup('test-e2e', [], 'file1.ceryle', dependencies=[])

    runner = TaskRunner([g1, g2, g3, g4])

    with util.std_capture() as (o, _):
        with pytest.raises(TaskDefinitionError):
            runner.run('vuild-foo')
        lines = o.getvalue().splitlines()
    print(lines)

    assert 'similar task groups are' in lines
    assert '    build-foo' in lines
    assert '    build-bar' in lines
    assert '    build-all' in lines
    assert '    test-e2e' not in lines


def test_run_tasks_fails(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    g1_run = mocker.patch.object(g1, 'run', return_value=(True, {}))
    mock.attach_mock(g1_run, 'g1_run')
    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])
    g2_run = mocker.patch.object(g2, 'run', return_value=(False, {}))
    mock.attach_mock(g2_run, 'g2_run')

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is False
    g2.run.assert_called_once()
    g1.run.assert_not_called()
    assert mock.mock_calls == [
        mocker.call.g2_run(dry_run=False, register={}),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', False),
    ]
    assert cache.register == {}


def test_run_tasks_fails_by_exception(mocker):
    mock = mocker.Mock()

    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    g1_run = mocker.patch.object(g1, 'run', side_effect=Exception('test'))
    mock.attach_mock(g1_run, 'g1_run')

    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])
    g2_run = mocker.patch.object(g2, 'run', return_value=(True, {}))
    mock.attach_mock(g2_run, 'g2_run')

    runner = TaskRunner([g1, g2])

    with pytest.raises(Exception):
        runner.run('g1')
    g2.run.assert_called_once()
    g1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g2_run(dry_run=False, register={}),
        mocker.call.g1_run(dry_run=False, register={}),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert cache.register == {}


def test_dry_run(mocker):
    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    mocker.patch.object(g1, 'run', return_value=(True, {}))
    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])
    mocker.patch.object(g2, 'run', return_value=(True, {}))

    runner = TaskRunner([g1, g2])

    assert runner.run('g1', dry_run=True) is True
    g2.run.assert_called_once_with(dry_run=True, register={})
    g1.run.assert_called_once_with(dry_run=True, register={})

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g2', False),
        ('g1', False),
    ]
    assert cache.register == {}


def test_run_task_with_stdout(mocker):
    g1 = TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2'])
    mocker.patch.object(g1, 'run', return_value=(True, {
        'g2': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }))

    g2 = TaskGroup('g2', [], 'file1.ceryle', dependencies=[])
    mocker.patch.object(g2, 'run', return_value=(True, {
        'g2': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }))

    runner = TaskRunner([g1, g2])

    assert runner.run('g1') is True
    g2.run.assert_called_once_with(dry_run=False, register={})
    g1.run.assert_called_once_with(dry_run=False, register={
        'g2': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    })

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


def test_run_skip_task_already_run(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], 'file1.ceryle', dependencies=['g2', 'g3'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], 'file1.ceryle', dependencies=['g4'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], 'file1.ceryle', dependencies=['g4'])

    g4_t1 = Task(Command('do some'), 'context')
    g4 = TaskGroup('g4', [g4_t1], 'file1.ceryle', dependencies=[])

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


def test_run_do_not_skip_if_not_allowed(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], 'file1.ceryle', dependencies=['g2', 'g3', 'g4', 'g4'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], 'file1.ceryle', dependencies=['g4'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], 'file1.ceryle', dependencies=['g4'])

    g4_t1 = Task(Command('do some'), 'context')
    g4 = TaskGroup('g4', [g4_t1], 'file1.ceryle', dependencies=[], allow_skip=False)

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
    assert g4_t1.run.call_count == 4
    g2_t1.run.assert_called_once()
    g3_t1.run.assert_called_once()
    g1_t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g4_t1_run(dry_run=False, inputs=[]),
        mocker.call.g2_t1_run(dry_run=False, inputs=[]),
        mocker.call.g4_t1_run(dry_run=False, inputs=[]),
        mocker.call.g3_t1_run(dry_run=False, inputs=[]),
        mocker.call.g4_t1_run(dry_run=False, inputs=[]),
        mocker.call.g4_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
    ]

    cache = runner.get_cache()
    assert cache.task_name == 'g1'
    assert cache.results == [
        ('g4', True),
        ('g2', True),
        ('g4', True),
        ('g3', True),
        ('g4', True),
        ('g4', True),
        ('g1', True),
    ]
    assert cache.register == {}


def test_run_skip_succeeded_tasks(mocker):
    mock = mocker.Mock()

    g1_t1 = Task(Command('do some'), 'context')
    g1 = TaskGroup('g1', [g1_t1], 'file1.ceryle', dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], 'file1.ceryle', dependencies=[])

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
    g1 = TaskGroup('g1', [g1_t1], 'file1.ceryle', dependencies=['g3'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], 'file1.ceryle', dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], 'file1.ceryle', dependencies=[])

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
    g1 = TaskGroup('g1', [g1_t1], 'file1.ceryle', dependencies=['g2'])

    g3_t1 = Task(Command('do some'), 'context')
    g3 = TaskGroup('g3', [g3_t1], 'file1.ceryle', dependencies=['g2'])

    g2_t1 = Task(Command('do some'), 'context')
    g2 = TaskGroup('g2', [g2_t1], 'file1.ceryle', dependencies=[])

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
