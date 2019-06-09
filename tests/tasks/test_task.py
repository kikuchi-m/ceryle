from ceryle import Command, ExecutionResult, Task


def test_run_succeeded(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    t = Task(executable, 'context')
    success = t.run()

    assert success is True
    executable.execute.assert_called_once_with(context='context')


def test_run_failed(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    t = Task(executable, 'context')
    success = t.run()

    assert success is False
    executable.execute.assert_called_once_with(context='context')
