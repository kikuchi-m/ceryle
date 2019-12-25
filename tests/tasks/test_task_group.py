import pytest

from ceryle import Command, Task, TaskGroup
from ceryle.tasks import TaskIOError
from ceryle.tasks.task import copy_register


def test_new_task_group():
    t1 = Task(Command('do some'), 'context')
    t2 = Task(Command('do awwsome'), 'context')
    tg = TaskGroup('new_task', [t1, t2], 'file1.ceryle')

    assert tg.name == 'new_task'
    assert tg.tasks == [t1, t2]
    assert tg.filename == 'file1.ceryle'


def test_new_task_group_deps():
    tg = TaskGroup('build', [], 'file1.ceryle', dependencies=['setup', 'pre-build'])
    assert tg.dependencies == ['setup', 'pre-build']


def test_run_tasks(mocker):
    mock = mocker.Mock()

    t1 = Task(Command('do some'), 'context')
    t2 = Task(Command('do some'), 'context')
    tg = TaskGroup('tg', [t1, t2], 'file1.ceryle')

    g1_t1_run = mocker.patch.object(t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')
    g1_t2_run = mocker.patch.object(t2, 'run', return_value=True)
    mock.attach_mock(g1_t2_run, 'g1_t2_run')

    res, reg = tg.run()

    assert res is True
    assert reg == {}
    t2.run.assert_called_once()
    t1.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t2_run(dry_run=False, inputs=[]),
    ]


def test_run_tasks_fails(mocker):
    mock = mocker.Mock()

    t1 = Task(Command('do some'), 'context')
    t2 = Task(Command('do some'), 'context')
    tg = TaskGroup('tg', [t1, t2], 'file1.ceryle')

    g1_t1_run = mocker.patch.object(t1, 'run', return_value=True)
    mock.attach_mock(g1_t1_run, 'g1_t1_run')
    g1_t2_run = mocker.patch.object(t2, 'run', return_value=False)
    mock.attach_mock(g1_t2_run, 'g1_t2_run')

    res, reg = tg.run()

    assert res is False
    assert reg == {}
    t1.run.assert_called_once()
    t2.run.assert_called_once()
    assert mock.mock_calls == [
        mocker.call.g1_t1_run(dry_run=False, inputs=[]),
        mocker.call.g1_t2_run(dry_run=False, inputs=[]),
    ]


def test_dry_run(mocker):
    t1 = Task(Command('do some'), 'context')
    t2 = Task(Command('do some'), 'context')
    tg = TaskGroup('tg', [t1, t2], 'file1.ceryle')

    mocker.patch.object(t1, 'run', return_value=True)
    mocker.patch.object(t2, 'run', return_value=True)

    res, reg = tg.run(dry_run=True)

    assert res is True
    assert reg == {}
    t2.run.assert_called_once_with(dry_run=True, inputs=[])
    t1.run.assert_called_once_with(dry_run=True, inputs=[])


def test_run_task_set_stdout_to_register(mocker):
    t1 = Task(Command('do some'), 'context', stdout='EXEC_STDOUT')
    mocker.patch.object(t1, 'stdout', return_value=['foo', 'bar'])
    mocker.patch.object(t1, 'stderr', return_value=[])
    mocker.patch.object(t1, 'run', return_value=True)
    tg = TaskGroup('tg', [t1], 'file1.ceryle', dependencies=[])

    res, reg = tg.run()

    assert res is True
    assert reg == {
        'tg': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }
    t1.run.assert_called_once_with(dry_run=False, inputs=[])
    t1.stdout.assert_called_once()
    t1.stderr.assert_not_called()


def test_run_task_set_stderr_to_register(mocker):
    t1 = Task(Command('do some'), 'context', stderr='EXEC_STDERR')
    mocker.patch.object(t1, 'stdout', return_value=[])
    mocker.patch.object(t1, 'stderr', return_value=['foo', 'bar'])
    mocker.patch.object(t1, 'run', return_value=True)
    tg = TaskGroup('tg', [t1], 'file1.ceryle', dependencies=[])

    res, reg = tg.run()

    assert res is True
    assert reg == {
        'tg': {
            'EXEC_STDERR': ['foo', 'bar'],
        },
    }
    t1.run.assert_called_once_with(dry_run=False, inputs=[])
    t1.stdout.assert_not_called()
    t1.stderr.assert_called_once()


def test_run_task_with_input_from_register(mocker):
    t1 = Task(Command('do some'), 'context', input=('another_tg', 'EXEC_STDOUT'))
    mocker.patch.object(t1, 'stdout', return_value=[])
    mocker.patch.object(t1, 'stderr', return_value=[])
    mocker.patch.object(t1, 'run', return_value=True)
    tg = TaskGroup('tg', [t1], 'file1.ceryle')

    register = {
        'another_tg': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }
    res, reg = tg.run(register=register)

    assert res is True
    assert reg == {
        'another_tg': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }
    t1.run.assert_called_once_with(dry_run=False, inputs=['foo', 'bar'])
    t1.stdout.assert_not_called()
    t1.stderr.assert_not_called()


def test_run_task_with_input_from_same_group(mocker):
    t1 = Task(Command('do some'), 'context', stdout='EXEC_STDOUT')
    mocker.patch.object(t1, 'stdout', return_value=['foo', 'bar'])
    mocker.patch.object(t1, 'stderr', return_value=[])
    mocker.patch.object(t1, 'run', return_value=True)

    t2 = Task(Command('do some'), 'context', input='EXEC_STDOUT')
    mocker.patch.object(t2, 'stdout', return_value=[])
    mocker.patch.object(t2, 'stderr', return_value=[])
    mocker.patch.object(t2, 'run', return_value=True)

    tg = TaskGroup('tg', [t1, t2], 'file1.ceryle')

    res, reg = tg.run()

    assert res is True
    assert reg == {
        'tg': {
            'EXEC_STDOUT': ['foo', 'bar'],
        },
    }
    t2.run.assert_called_once_with(dry_run=False, inputs=['foo', 'bar'])
    t2.stdout.assert_not_called()
    t2.stderr.assert_not_called()
    t1.run.assert_called_once_with(dry_run=False, inputs=[])
    t1.stdout.assert_called_once()
    t1.stderr.assert_not_called()


def test_run_failed_by_invalid_io(mocker):
    t1 = Task(Command('do some'), 'context', input='EXEC_STDOUT')
    mocker.patch.object(t1, 'run', return_value=True)
    tg = TaskGroup('tg', [t1], 'file1.ceryle')

    with pytest.raises(TaskIOError) as ex:
        tg.run()
    t1.run.assert_not_called()
    assert str(ex.value) == 'EXEC_STDOUT is required by a task in tg, but not registered'


def test_copy_register():
    reg1 = {
        'g1': {
            'o1': ['a', 'b'],
            'o2': ['c'],
        },
        'g2': {
            'o1': ['d'],
            'o2': ['e', 'f'],
            'o3': ['g'],
        },
    }

    reg2 = copy_register(reg1)

    assert reg1 == reg2
    assert reg1 is not reg2
    assert reg1['g1'] is not reg2['g1']
    assert reg1['g2'] is not reg2['g2']
