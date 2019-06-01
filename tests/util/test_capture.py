import sys

from ceryle.util.capture import std_capture


def test_capture_stdout():
    with std_capture() as (o, _):
        print('foo')
        print('bar')
        assert ['foo', 'bar'] == o.getvalue().splitlines()


def test_capture_stderr():
    with std_capture() as (o, e):
        print('foo')
        print('bar', file=sys.stderr)
        assert ['foo'] == o.getvalue().splitlines()
        assert ['bar'] == e.getvalue().splitlines()
