import pytest

import ceryle.commands.builtin as builtin
from ceryle import Command, Executable, ExecutionResult


def test_expect_fail_raises():
    with pytest.raises(TypeError):
        builtin.expect_fail('not an executable')

    with pytest.raises(TypeError):
        builtin.expect_fail(None)


def test_expect_fail_str(mocker):
    cmd = Command('test 1')
    exe_xfail = builtin.expect_fail(cmd)
    assert str(exe_xfail) == f'fail({cmd})'


def test_expect_fail_returns_failure(mocker):
    cmd = Command('test 1')
    cmd_res = ExecutionResult(0, stdout=['out'], stderr=['err'])
    mocker.patch.object(cmd, 'execute', return_value=cmd_res)

    exe_xfail = builtin.expect_fail(cmd)
    assert isinstance(exe_xfail, Executable) is True

    res = exe_xfail.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 1
    assert res.stdout == ['out']
    assert res.stderr == ['err']
    cmd.execute.assert_called_once_with(context='context', inputs=['a'])


def test_expect_fail_returns_success(mocker):
    cmd = Command('test 1')
    cmd_res = ExecutionResult(255, stdout=['out'], stderr=['err'])
    mocker.patch.object(cmd, 'execute', return_value=cmd_res)

    exe_xfail = builtin.expect_fail(cmd)
    assert isinstance(exe_xfail, Executable) is True

    res = exe_xfail.execute(context='context', inputs=['a'])
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0
    assert res.stdout == ['out']
    assert res.stderr == ['err']
    cmd.execute.assert_called_once_with(context='context', inputs=['a'])
