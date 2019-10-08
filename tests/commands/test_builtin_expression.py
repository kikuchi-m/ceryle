import pytest

import ceryle.commands.buildin as buildin
from ceryle import Executable, ExecutionResult, TaskDefinitionError
from ceryle.dsl.support import Arg


@pytest.mark.parametrize(
    'code,return_code',
    [('1 == 1', 0), ('1 == 2', 1)])
def test_expression(code, return_code):
    exp = buildin.expression(code)

    assert isinstance(exp, Executable) is True

    res = exp.execute()

    assert isinstance(res, ExecutionResult)
    assert res.return_code == return_code


def test_expression_with_arg():
    exp = buildin.expression('2 == ' + Arg('FOO', {'FOO': '2'}))

    assert isinstance(exp, Executable) is True

    res = exp.execute()

    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0


def test_expression_returns_not_bool():
    with pytest.raises(TaskDefinitionError) as e:
        buildin.expression('1').execute()
    assert str(e.value) == 'return boolean value by expression: [1]'
