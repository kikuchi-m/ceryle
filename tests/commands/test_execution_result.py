import pytest

from ceryle import ExecutionResult
from ceryle.util.printutils import Output


@pytest.mark.parametrize(
    'rc, o, e', [
        ('a', [], []),
        (0, 1, []),
        (0, 'a', []),
        (0, [], 1),
        (0, [], 'a'),
    ])
def test_raise_when_invalid_type(rc, o, e):
    with pytest.raises(TypeError):
        ExecutionResult(rc, o, e)


@pytest.mark.parametrize(
    'rc, in_o, in_e, x_o, x_e', [
        (0, [], [], [], []),
        (127, [], [], [], []),
        (0,
         ['aa', 'bb'], ['xx', 'yy'],
         ['aa', 'bb'], ['xx', 'yy']),
        (0,
         Output.from_lines(['aa', 'bb']), [],
         ['aa', 'bb'], []),
        (0,
         [], Output.from_lines(['xx', 'yy']),
         [], ['xx', 'yy']),
    ])
def test_create_instance(rc, in_o, in_e, x_o, x_e):
    res = ExecutionResult(rc, in_o, in_e)

    assert res.return_code == rc
    assert res.stdout == x_o
    assert res.stderr == x_e


@pytest.mark.parametrize(
    'in_o, in_e, x_o, x_e', [
        ([], [], [], []),
        (['aa', 'bb'], ['xx', 'yy'], ['aa', 'bb'], ['xx', 'yy']),
        (Output.from_lines(['aa', 'bb']), [], ['aa', 'bb'], []),
        ([], Output.from_lines(['xx', 'yy']), [], ['xx', 'yy']),
    ])
def test_get_output(in_o, in_e, x_o, x_e):
    res = ExecutionResult(0, in_o, in_e)

    o = res.get_output(ExecutionResult.STDOUT)
    assert isinstance(o, Output)
    assert o.lines() == x_o

    e = res.get_output(ExecutionResult.STDERR)
    assert isinstance(e, Output)
    assert e.lines() == x_e
