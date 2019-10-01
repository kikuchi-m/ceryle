import pytest

from ceryle import Command, ExecutionResult, Task
from ceryle import IllegalOperation


def test_raise_if_unacceptable_args():
    with pytest.raises(TypeError):
        Task(None, 'context')

    with pytest.raises(TypeError):
        Task('not an executable', 'context')

    with pytest.raises(TypeError):
        Task(Command('do some', None))

    with pytest.raises(TypeError):
        Task(Command('do some', 1))


def test_run_succeeded(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    t = Task(executable, 'context')
    success = t.run()

    assert success is True
    executable.execute.assert_called_once_with(context='context', inputs=[])
    assert t.stdout() == []
    assert t.stderr() == []


def test_run_failed(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    t = Task(executable, 'context')
    success = t.run()

    assert success is False
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_run_ignore_failure(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(255))

    t = Task(executable, 'context', ignore_failure=True)
    success = t.run()

    assert success is True
    executable.execute.assert_called_once()


def test_dry_run(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    t = Task(executable, 'context')
    success = t.run(dry_run=True)

    assert success is True
    executable.execute.assert_not_called()
    assert t.stdout() == []
    assert t.stderr() == []


def test_store_stds(mocker):
    executable = Command('do some')
    res = ExecutionResult(0, stdout=['std', 'out'], stderr=['err'])
    mocker.patch.object(executable, 'execute', return_value=res)

    t = Task(executable, 'context', stdout='EXEC_STDOUT', stderr='EXEC_STDERR')
    success = t.run()

    assert success is True
    executable.execute.assert_called_once_with(context='context', inputs=[])
    assert t.stdout_key == 'EXEC_STDOUT'
    assert t.stderr_key == 'EXEC_STDERR'
    assert t.stdout() == ['std', 'out']
    assert t.stderr() == ['err']


def test_run_with_input(mocker):
    executable = Command('do some')
    res = ExecutionResult(0)
    mocker.patch.object(executable, 'execute', return_value=res)

    t = Task(executable, 'context', input='EXEC_INPUT')
    success = t.run(inputs=['foo', 'bar'])

    assert success is True
    executable.execute.assert_called_once_with(context='context', inputs=['foo', 'bar'])
    assert t.input_key == 'EXEC_INPUT'


def test_get_stds_raise_before_run(mocker):
    executable = Command('do some')
    res = ExecutionResult(0, stdout=['std', 'out'], stderr=['err'])
    mocker.patch.object(executable, 'execute', return_value=res)

    t = Task(executable, 'context')

    with pytest.raises(IllegalOperation) as ex1:
        t.stdout()
    assert str(ex1.value) == 'task is not run yet'

    with pytest.raises(IllegalOperation) as ex2:
        t.stderr()
    assert str(ex2.value) == 'task is not run yet'
