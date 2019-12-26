import pytest

from ceryle import Command, ExecutionResult, Task
from ceryle import IllegalOperation


def test_raise_if_unacceptable_args():
    with pytest.raises(TypeError):
        Task(None)

    with pytest.raises(TypeError):
        Task('not an executable')


def test_run_succeeded(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    t = Task(executable)
    success = t.run('context')

    assert success is True
    executable.execute.assert_called_once_with(context='context', inputs=[])
    assert t.stdout() == []
    assert t.stderr() == []


def test_run_failed(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    t = Task(executable)
    success = t.run('context')

    assert success is False
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_run_ignore_failure(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(255))

    t = Task(executable, ignore_failure=True)
    success = t.run('context')

    assert success is True
    executable.execute.assert_called_once()


def test_dry_run(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    t = Task(executable)
    success = t.run('context', dry_run=True)

    assert success is True
    executable.execute.assert_not_called()
    assert t.stdout() == []
    assert t.stderr() == []


def test_store_stds(mocker):
    executable = Command('do some')
    res = ExecutionResult(0, stdout=['std', 'out'], stderr=['err'])
    mocker.patch.object(executable, 'execute', return_value=res)

    t = Task(executable, stdout='EXEC_STDOUT', stderr='EXEC_STDERR')
    success = t.run('context')

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

    t = Task(executable, input='EXEC_INPUT')
    success = t.run('context', inputs=['foo', 'bar'])

    assert success is True
    executable.execute.assert_called_once_with(context='context', inputs=['foo', 'bar'])
    assert t.input_key == 'EXEC_INPUT'


def test_get_stds_raise_before_run(mocker):
    executable = Command('do some')
    res = ExecutionResult(0, stdout=['std', 'out'], stderr=['err'])
    mocker.patch.object(executable, 'execute', return_value=res)

    t = Task(executable)

    with pytest.raises(IllegalOperation) as ex1:
        t.stdout()
    assert str(ex1.value) == 'task is not run yet'

    with pytest.raises(IllegalOperation) as ex2:
        t.stderr()
    assert str(ex2.value) == 'task is not run yet'


def test_run_conditional_on_true(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    condition_exe = Command('test condition')
    mocker.patch.object(condition_exe, 'execute', return_value=ExecutionResult(0))

    t = Task(executable, conditional_on=condition_exe)

    assert t.run('context') is True
    condition_exe.execute.assert_called_once_with(context='context', inputs=[])
    executable.execute.assert_called_once()
    assert t.stdout() == []
    assert t.stderr() == []


def test_run_conditional_on_false(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    condition_exe = Command('test condition')
    mocker.patch.object(condition_exe, 'execute', return_value=ExecutionResult(255))

    t = Task(executable, conditional_on=condition_exe)

    assert t.run('context') is True
    condition_exe.execute.assert_called_once_with(context='context', inputs=[])
    executable.execute.assert_not_called()
    assert t.stdout() == []
    assert t.stderr() == []


@pytest.mark.parametrize(
    'condition', [
        (True),
        (False),
    ])
def test_run_conditional_on_boolean(mocker, condition):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    t = Task(executable, conditional_on=condition)

    assert t.run('context') is True
    if condition:
        executable.execute.assert_called_once()
    else:
        executable.execute.assert_not_called()


@pytest.mark.parametrize(
    'conditional_on, dry_run, inputs, exe_calls', [
        (0, True, [], 0),
        (1, True, [], 0),
        (0, False, ['a'], 1),
        (0, True, ['a'], 0),
    ], ids=str)
def test_run_conditional_by_dry_run_with_inputs(mocker, conditional_on, dry_run, inputs, exe_calls):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    condition_exe = Command('test condition')
    mocker.patch.object(condition_exe, 'execute', return_value=ExecutionResult(conditional_on))

    t = Task(executable, conditional_on=condition_exe)

    assert t.run('context', dry_run=dry_run, inputs=inputs) is True
    if dry_run:
        condition_exe.execute.assert_not_called()
        executable.execute.assert_not_called()
    else:
        condition_exe.execute.assert_called_once_with(context='context', inputs=inputs)
        executable.execute.assert_called_once()
