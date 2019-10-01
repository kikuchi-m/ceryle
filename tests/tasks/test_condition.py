import pytest

from ceryle import Condition, Command, ExecutionResult


def test_condition_invalid_condition_value():
    with pytest.raises(ValueError):
        Condition(None, 'context')

    with pytest.raises(ValueError):
        Condition('unknown pattern', 'context')


def test_condition_test_by_successful_executable(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    condition = Condition(executable, 'context')
    assert condition.test() is True
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_condition_test_by_unsuccessful_executable(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    condition = Condition(executable, 'context')
    assert condition.test() is False
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_condition_test_predefined_no_input(mocker):
    condition = Condition('no_input', 'context')
    assert condition.test() is True
    assert condition.test(inputs=['a']) is False
