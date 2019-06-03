from ceryle import Command, Task

def test_run_succeeded(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=0)

    t = Task(executable)
    success = t.run()

    assert success
    executable.execute.assert_called_once_with()


def test_run_failed(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=1)

    t = Task(executable)
    success = t.run()

    assert not success
    executable.execute.assert_called_once_with()
