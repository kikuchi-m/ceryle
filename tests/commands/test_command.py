import os
import pathlib
import pytest
import re
import shutil
import tempfile

from ceryle import Command, CommandFormatError
from ceryle.dsl.support import Arg, Env
from ceryle.util import std_capture

FILE_DIR = os.path.dirname(__file__)


def test_new_command():
    # command part strings by list
    command = Command(['ls', '-a'])
    assert command.cmd == ['ls', '-a']
    assert str(command) == '[ls -a]'

    # sysntax sugar
    command = Command('ls -a')
    assert command.cmd == ['ls', '-a']
    assert str(command) == '[ls -a]'

    # sysntax sugar with double quoted
    command = Command('echo "a b"')
    assert command.cmd == ['echo', 'a b']
    assert str(command) == '[echo "a b"]'

    command = Command(' foo "a b" c  d  ')
    assert command.cmd == ['foo', 'a b', 'c', 'd']
    assert str(command) == '[foo "a b" c d]'

    # env and arg
    command = Command(['do-some', Env('FOO'), Arg('BAR', {})])
    assert str(command) == '[do-some env(FOO) arg(BAR)]'


def test_raise_if_invalid_command():
    with pytest.raises(TypeError):
        Command(None)

    with pytest.raises(TypeError):
        Command(1)

    with pytest.raises(TypeError):
        Command(object())

    with pytest.raises(CommandFormatError, match=r'invalid command format: \[a b "c d\]'):
        Command('a b "c d')


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


def test_execute_command_return_stdout():
    command = Command('echo foo')
    result = command.execute()
    assert result.return_code == 0
    assert len(result.stdout) == 1
    assert result.stdout[0].rstrip() == 'foo'
    assert len(result.stderr) == 0


def test_execute_command_return_stderr():
    command = Command('./scripts/stderr.sh', cwd=FILE_DIR)
    result = command.execute()
    assert result.return_code == 3
    assert len(result.stdout) == 0
    assert len(result.stderr) == 1
    assert result.stderr[0].rstrip() == 'sample error'


def test_execute_with_inputs():
    with std_capture() as (o, e):
        command = Command(['cat'])
        result = command.execute(inputs=['foo', 'bar'], timeout=3)
        assert result.return_code == 0
        assert len(result.stdout) == 2
        assert result.stdout[0].rstrip() == 'foo'
        assert result.stdout[1].rstrip() == 'bar'

        lines = [l.rstrip() for l in o.getvalue().splitlines()]
        assert lines == ['foo', 'bar']


def test_execute_with_inputs_as_args():
    with std_capture() as (o, e):
        command = Command(['echo'], inputs_as_args=True)
        result = command.execute(inputs=['foo', 'bar'], timeout=3)
        assert result.return_code == 0
        assert len(result.stdout) == 1
        assert result.stdout[0].rstrip() == 'foo bar'

        lines = [l.rstrip() for l in o.getvalue().splitlines()]
        assert lines == ['foo bar']


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


def test_execute_with_environment_variables():
    no_env = Command('./scripts/env_test.sh', cwd=FILE_DIR)
    no_env_res = no_env.execute()

    assert no_env_res.return_code == 0
    assert no_env_res.stdout == ['']

    env = {'CERYLE_ENV_TEST': 'ceryle environment variable test'}
    with_env = Command('./scripts/env_test.sh', cwd=FILE_DIR, env=env)
    with_env_res = with_env.execute()

    assert with_env_res.return_code == 0
    assert with_env_res.stdout == ['ceryle environment variable test']


def test_execute_with_environment_variables_from_envs(mocker):
    mocker.patch.dict('os.environ', {'FOO': 'ceryle environment variable test'})

    env = {'CERYLE_ENV_TEST': Env('FOO')}
    command = Command('./scripts/env_test.sh', cwd=FILE_DIR, env=env)
    res = command.execute()

    assert res.return_code == 0
    assert res.stdout == ['ceryle environment variable test']


def test_execute_with_environment_variables_from_args(mocker):
    env = {'CERYLE_ENV_TEST': Arg('FOO', {'FOO': 'ceryle environment variable test'})}
    command = Command('./scripts/env_test.sh', cwd=FILE_DIR, env=env)
    res = command.execute()

    assert res.return_code == 0
    assert res.stdout == ['ceryle environment variable test']


def test_with_envs_and_args(mocker):
    mocker.patch.dict('os.environ', {'ENV1': 'AAA'})
    args = {'ARG1': 'BBB'}
    command = Command(['echo', Env('ENV1'), Arg('ARG1', args)])
    res = command.execute()
    assert res.return_code == 0
    assert res.stdout == ['AAA BBB']
