import os
import pathlib
import pytest
import re
import shutil
import tempfile

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
        assert command.execute().return_code == 0
        assert o.getvalue().rstrip() == 'foo'

    with std_capture() as (o, e):
        command = Command('echo foo')
        assert command.execute().return_code == 0
        assert o.getvalue().rstrip() == 'foo'

    with std_capture() as (o, e):
        command = Command('echo "foo bar"')
        assert command.execute().return_code == 0
        assert o.getvalue().rstrip() == 'foo bar'


def test_execute_script():
    with std_capture() as (o, e):
        command = Command('./scripts/sample1.sh', cwd=FILE_DIR)
        assert command.execute().return_code == 0
        lines = [l.rstrip() for l in o.getvalue().splitlines()]
        assert lines == ['hello', 'good-by']


def test_execute_script_with_error():
    with std_capture() as (o, e):
        command = Command('./scripts/stderr.sh', cwd=FILE_DIR)
        assert command.execute().return_code == 3
        assert re.match('.*sample error.*', e.getvalue().rstrip())


def test_execute_with_context():
    with tempfile.TemporaryDirectory() as tmpd:
        context = pathlib.Path(tmpd)
        script = pathlib.Path(context, 'sample1.sh')
        shutil.copy(
            str(pathlib.Path(FILE_DIR, 'scripts', 'sample1.sh')),
            str(script))

        with std_capture() as (o, e):
            command = Command('./sample1.sh')
            assert command.execute(context=str(context)).return_code == 0
            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['hello', 'good-by']


def test_execute_with_context_and_cwd():
    with tempfile.TemporaryDirectory() as tmpd:
        context = pathlib.Path(tmpd)
        script = pathlib.Path(context, 'aa', 'sample1.sh')
        script.parent.mkdir()
        shutil.copy(
            str(pathlib.Path(FILE_DIR, 'scripts', 'sample1.sh')),
            str(script))

        with std_capture() as (o, e):
            command = Command('./sample1.sh', cwd='aa')
            assert command.execute(context=str(context)).return_code == 0
            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['hello', 'good-by']


def test_execute_absolute_cwd():
    with tempfile.TemporaryDirectory() as tmpd1, tempfile.TemporaryDirectory() as tmpd2:
        context = pathlib.Path(tmpd1)
        cwd = pathlib.Path(tmpd2, 'aa')
        cwd.mkdir()
        script = pathlib.Path(cwd, 'sample1.sh')
        shutil.copy(
            str(pathlib.Path(FILE_DIR, 'scripts', 'sample1.sh')),
            str(script))

        with std_capture() as (o, e):
            command = Command('./sample1.sh', cwd=str(cwd))
            assert command.execute(context=str(context)).return_code == 0
            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['hello', 'good-by']
