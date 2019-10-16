import pytest

import ceryle.commands.buildin as buildin
from ceryle import Command, Executable, ExecutionResult


def test_execute_all_raises():
    with pytest.raises(TypeError):
        exec_all = buildin.execute_all(Command('do some'), 'not an executable')

    with pytest.raises(ValueError, match=r'one or more executables are required'):
        buildin.execute_all()


def test_execute_all(mocker):
    mock = mocker.Mock()

    cmd1 = Command('test 1')
    mocker.patch.object(cmd1, 'execute', return_value=ExecutionResult(0))
    mock.attach_mock(cmd1.execute, 'cmd1_execute')

    cmd2 = Command('test 2')
    mocker.patch.object(cmd2, 'execute', return_value=ExecutionResult(0))
    mock.attach_mock(cmd2.execute, 'cmd2_execute')

    exec_all = buildin.execute_all(cmd1, cmd2)
    assert isinstance(exec_all, Executable) is True

    res = exec_all.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0
    assert mock.mock_calls == [
        mocker.call.cmd1_execute(context='context', inputs=['a']),
        mocker.call.cmd2_execute(context='context', inputs=['a']),
    ]


def test_execute_all_fails(mocker):
    mock = mocker.Mock()

    cmd1 = Command('test 1')
    mocker.patch.object(cmd1, 'execute', return_value=ExecutionResult(1))
    mock.attach_mock(cmd1.execute, 'cmd1_execute')

    cmd2 = Command('test 2')
    mocker.patch.object(cmd2, 'execute', return_value=ExecutionResult(0))
    mock.attach_mock(cmd2.execute, 'cmd2_execute')

    exec_all = buildin.execute_all(cmd1, cmd2)
    assert isinstance(exec_all, Executable) is True

    res = exec_all.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 1
    assert mock.mock_calls == [
        mocker.call.cmd1_execute(context='context', inputs=['a']),
    ]
