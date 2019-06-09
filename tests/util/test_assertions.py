import pytest

from ceryle import Command, Executable
from ceryle.util import assert_type


def test_raise_if_not_type():
    with pytest.raises(TypeError, match=r'not a type; .*'):
        assert_type('foo', 'not a type')


def test_raise_if_not_match_type():
    with pytest.raises(TypeError, match=r'not matched to any type int; actual: str'):
        assert_type('foo', int)

    with pytest.raises(TypeError, match=r'not matched to any type Foo; actual: str'):
        assert_type('foo', Foo)

    with pytest.raises(TypeError, match=r'not matched to any type Executable; actual: str'):
        assert_type('foo', Executable)


def test_pass_assertion():
    assert assert_type('foo', str) == 'foo'

    foo = Foo()
    assert assert_type(foo, Foo) == foo

    bar = Bar()
    assert assert_type(bar, Foo) == bar

    cmd = Command('do some')
    assert assert_type(cmd, Executable) == cmd


class Foo:
    pass


class Bar(Foo):
    pass
