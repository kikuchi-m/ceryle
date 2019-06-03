import  pytest

from ceryle import Command, Executable
from ceryle.util import assert_type


def test_raise_if_not_type():
    with pytest.raises(TypeError, match=r'2nd argument must be a type; passed .*'):
        assert_type('foo', 'not a type')


def test_raise_if_not_match_type():
    with pytest.raises(TypeError, match=r'not matched to type int; actual: str'):
        assert_type('foo', int)

    with pytest.raises(TypeError, match=r'not matched to type Foo; actual: str'):
        assert_type('foo', Foo)

    with pytest.raises(TypeError, match=r'not matched to type Executable; actual: str'):
        assert_type('foo', Executable)


def test_pass_assertion():
    assert_type('foo', str)

    assert_type(Foo(), Foo)
    assert_type(Bar(), Foo)
    assert_type(Command('do some'), Executable)


class Foo:
    pass


class Bar(Foo):
    pass
