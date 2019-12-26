import pytest

from ceryle import Condition, Command, ExecutionResult


def test_condition_invalid_condition_value():
    with pytest.raises(TypeError):
        Condition(None)

    with pytest.raises(TypeError):
        Condition('unknown pattern')


def test_condition_test_by_successful_executable(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(0))

    condition = Condition(executable)
    assert condition.test(context='context') is True
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_condition_test_by_unsuccessful_executable(mocker):
    executable = Command('do some')
    mocker.patch.object(executable, 'execute', return_value=ExecutionResult(1))

    condition = Condition(executable)
    assert condition.test(context='context') is False
    executable.execute.assert_called_once_with(context='context', inputs=[])


def test_condition_test_predefined_no_input(mocker):
    condition = Condition(Condition.NO_INPUT)
    assert condition.test(context='context') is True
    assert condition.test(context='context', inputs=['a']) is False


def test_condition_test_predefined_has_input(mocker):
    condition = Condition(Condition.HAS_INPUT)
    assert condition.test(context='context') is False
    assert condition.test(context='context', inputs=['a']) is True


def test_condition_test_bool():
    condition1 = Condition(True)
    assert condition1.test(context='context') is True

    condition2 = Condition(False)
    assert condition2.test(context='context') is False


def test_condition_test_bool_with_dry_run():
    condition1 = Condition(True)
    assert condition1.test(context='context', dry_run=True) is True

    condition2 = Condition(False)
    assert condition2.test(context='context', dry_run=True) is True


def test_condition_test_by_executable_with_dry_run(mocker):
    # successful executable
    executable1 = Command('do some')
    mocker.patch.object(executable1, 'execute', return_value=ExecutionResult(0))

    condition = Condition(executable1)
    assert condition.test(context='context', dry_run=True) is True
    executable1.execute.assert_not_called()

    # unsuccessful executable
    executable2 = Command('do some')
    mocker.patch.object(executable2, 'execute', return_value=ExecutionResult(255))

    condition = Condition(executable2)
    assert condition.test(context='context', dry_run=True) is True
    executable2.execute.assert_not_called()


@pytest.fixture(params=[
    Condition.NO_INPUT,
    Condition.HAS_INPUT,
])
def predefined_condition(request):
    return request.param


@pytest.fixture(params=[
    [],
    ['a'],
], ids=lambda inputs: f'inputs{inputs}')
def arg_inputs(request):
    return request.param


def test_condition_test_by_predefined_with_dry_run(predefined_condition, arg_inputs):
    condition = Condition(predefined_condition)
    assert condition.test(context='context', dry_run=True) is True
    assert condition.test(context='context', dry_run=True, inputs=arg_inputs) is True
