from ceryle.util import getin


def test_getin():
    assert getin({'a': 1}, 'a') == 1
    assert getin({'a': 1}, 'b') is None
    assert getin({'a': 1}, 'a', 'b') is None

    assert getin({0: 1}, 0) == 1

    assert getin({'a': {'b': 2}}, 'a', 'b') == 2
    assert getin({'a': {'b': 2}}, 'a', 'c') is None
    assert getin({'a': {'b': 2}}, 'a', 'b', 'c') is None


def test_getin_returns_default():
    assert getin({'a': 1}, 'b', default=-1) == -1
    assert getin({'a': 1}, 'a', 'b', default=-1) == -1
    assert getin({'a': {'b': 2}}, 'a', 'b', 'c', default=-1) == -1
