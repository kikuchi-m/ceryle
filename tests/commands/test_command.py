import os
import pytest
import re

from ceryle import Command
from ceryle.util import std_capture

FILE_DIR = os.path.dirname(__file__)


def test_new_command():
    # command part strings by list
    command = Command(['ls', '-a'])
    assert command.cmd == ['ls', '-a']

    # sysntax sugar
    command = Command('ls -a')
    assert command.cmd == ['ls', '-a']

    # sysntax sugar with double quoted
    command = Command('echo "a b"')
    assert command.cmd == ['echo', 'a b']

    command = Command(' foo "a b" c  d  ')
    assert command.cmd == ['foo', 'a b', 'c', 'd']


def test_raise_if_invalid_command():
    with pytest.raises(TypeError):
        Command(None)

    with pytest.raises(TypeError):
        Command(1)

    with pytest.raises(TypeError):
        Command(object())


def test_execute_command():
    with std_capture() as (o, e):
        command = Command('echo foo')
        command.execute()
        assert o.getvalue().rstrip() == 'foo'

    with std_capture() as (o, e):
        command = Command('echo foo')
        command.execute()
        assert o.getvalue().rstrip() == 'foo'

    with std_capture() as (o, e):
        command = Command('echo "foo bar"')
        command.execute()
        assert o.getvalue().rstrip() == 'foo bar'


def test_execute_script():
    with std_capture() as (o, e):
        command = Command('./scripts/sample1.sh', cwd=FILE_DIR)
        command.execute()
        lines = [l.rstrip() for l in o.getvalue().splitlines()]
        assert lines == ['hello', 'good-by']


def test_execute_script_with_error():
    with std_capture() as (o, e):
        command = Command('./scripts/stderr.sh', cwd=FILE_DIR)
        command.execute()
        assert re.match('.*sample error.*', e.getvalue().rstrip())
