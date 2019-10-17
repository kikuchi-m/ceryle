import pytest

import ceryle.commands.buildin as buildin
from ceryle import Command, Executable, ExecutionResult


def test_execute_any_raises():
    with pytest.raises(TypeError):
        buildin.execute_any(Command('do some'), 'not an executable')

    with pytest.raises(ValueError, match=r'one or more executables are required'):
        buildin.execute_any()


def test_execute_any_str(mocker):
    cmd1 = Command('test 1')
    cmd2 = Command('test 2')
    exec_any = buildin.execute_any(cmd1, cmd2)
    assert str(exec_any) == f'any({cmd1}, {cmd2})'


def test_execute_any(mocker):
    mock = mocker.Mock()

    cmd1 = Command('test 1')
    mocker.patch.object(cmd1, 'execute', return_value=ExecutionResult(0))
    mock.attach_mock(cmd1.execute, 'cmd1_execute')

    cmd2 = Command('test 2')
    mocker.patch.object(cmd2, 'execute', return_value=ExecutionResult(0))
    mock.attach_mock(cmd2.execute, 'cmd2_execute')

    exec_any = buildin.execute_any(cmd1, cmd2)
    assert isinstance(exec_any, Executable) is True

    res = exec_any.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0
    assert mock.mock_calls == [
        mocker.call.cmd1_execute(context='context', inputs=['a']),
    ]


def test_execute_any_fails(mocker):
    mock = mocker.Mock()

    cmd1 = Command('test 1')
    mocker.patch.object(cmd1, 'execute', return_value=ExecutionResult(1))
    mock.attach_mock(cmd1.execute, 'cmd1_execute')

    cmd2 = Command('test 2')
    mocker.patch.object(cmd2, 'execute', return_value=ExecutionResult(2))
    mock.attach_mock(cmd2.execute, 'cmd2_execute')

    exec_any = buildin.execute_any(cmd1, cmd2)
    assert isinstance(exec_any, Executable) is True

    res = exec_any.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 2
    assert mock.mock_calls == [
        mocker.call.cmd1_execute(context='context', inputs=['a']),
        mocker.call.cmd2_execute(context='context', inputs=['a']),
    ]
