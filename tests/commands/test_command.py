import os
import pathlib
import platform
import re
import shutil
import tempfile

import pytest

from ceryle import Command, CommandFormatError
from ceryle.dsl.support import Arg, Env, PathArg
from ceryle.util import std_capture

FILE_DIR = os.path.dirname(__file__)


def stub_env():
    return Env('FOO')


def stub_arg():
    return Arg('BAR', {})


def stub_path_arg():
    return PathArg('a', 'b')


@pytest.mark.parametrize(
    'cmd_in, cmd, cmd_str', [
        (['ls', '-a'], ['ls', '-a'], '[ls -a]'),
        ('ls -a', ['ls', '-a'], '[ls -a]'),
        # syntax sugar with double quoted
        ('echo "a b"', ['echo', 'a b'], '[echo "a b"]'),
        (' foo "a b" c  d  ', ['foo', 'a b', 'c', 'd'], '[foo "a b" c d]'),
        # with escape sequence
        ('echo a\\"b', ['echo', 'a\\"b'], '[echo a\\"b]'),
        ('echo a \\"b', ['echo', 'a', '\\"b'], '[echo a \\"b]'),
        ('echo a b\\"', ['echo', 'a', 'b\\"'], '[echo a b\\"]'),
        ('echo a \\"', ['echo', 'a', '\\"'], '[echo a \\"]'),
        ('echo a\\"b c', ['echo', 'a\\"b', 'c'], '[echo a\\"b c]'),
        ('echo a\\"b c "d e"', ['echo', 'a\\"b', 'c', 'd e'], '[echo a\\"b c "d e"]'),
        # env and arg
        (['do-some', stub_env(), stub_arg(), stub_path_arg()],
         ['do-some', stub_env(), stub_arg(), stub_path_arg()],
         f'[do-some {stub_env()} {stub_arg()} {stub_path_arg()}]'),
        (stub_env(), [stub_env()], f'[{stub_env()}]'),
        (stub_arg(), [stub_arg()], f'[{stub_arg()}]'),
        (stub_path_arg(), [stub_path_arg()], f'[{stub_path_arg()}]'),
    ])
def test_new_command(cmd_in, cmd, cmd_str):
    command = Command(cmd_in)
    assert command.cmd == cmd
    assert str(command) == cmd_str


def test_raise_if_invalid_command():
    with pytest.raises(TypeError):
        Command(None)

    with pytest.raises(TypeError):
        Command(1)

    with pytest.raises(TypeError):
        Command(object())

    with pytest.raises(CommandFormatError, match=r'invalid command format: \[a b "c d\]'):
        Command('a b "c d')


class TestAnyPlatform:
    def test_execute_script(self):
        with std_capture() as (o, e):
            command = Command('./scripts/sample1', cwd=FILE_DIR)
            assert command.execute().return_code == 0
            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['hello', 'good-bye']

    def test_execute_script_with_error(self):
        with std_capture() as (o, e):
            command = Command('./scripts/stderr', cwd=FILE_DIR)
            assert command.execute().return_code == 3
            assert re.match('.*sample error.*', e.getvalue().rstrip())

    def test_execute_command_return_stdout(self):
        command = Command('echo foo')
        result = command.execute()
        assert result.return_code == 0
        assert len(result.stdout) == 1
        assert result.stdout[0].rstrip() == 'foo'
        assert len(result.stderr) == 0

    def test_execute_command_return_stderr(self):
        command = Command('./scripts/stderr', cwd=FILE_DIR)
        result = command.execute()
        assert result.return_code == 3
        assert len(result.stdout) == 0
        assert len(result.stderr) == 1
        assert result.stderr[0].rstrip() == 'sample error'

    def test_execute_script_quiet(self):
        with std_capture() as (o, e):
            command = Command('./scripts/sample1', cwd=FILE_DIR, quiet=True)
            result = command.execute()
            assert result.return_code == 0
            assert result.stdout == ['hello', 'good-bye']
            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == []

    def test_execute_script_quiet_with_error(self):
        with std_capture() as (o, e):
            command = Command('./scripts/stderr', cwd=FILE_DIR, quiet=True)
            assert command.execute().return_code == 3
            assert re.match('.*sample error.*', e.getvalue().rstrip())

    def test_execute_with_inputs_as_args(self):
        with std_capture() as (o, e):
            command = Command(['echo'], inputs_as_args=True)
            result = command.execute(inputs=['foo', 'bar'], timeout=3)
            assert result.return_code == 0
            assert len(result.stdout) == 1
            assert result.stdout[0].rstrip() == 'foo bar'

            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['foo bar']

    def test_execute_with_context(self):
        with tempfile.TemporaryDirectory() as tmpd:
            context = pathlib.Path(tmpd)
            for s in ['sample1', 'sample1.bat']:
                script = pathlib.Path(context, s)
                shutil.copy(
                    str(pathlib.Path(FILE_DIR, 'scripts', s)),
                    str(script))

            with std_capture() as (o, e):
                command = Command('./sample1')
                assert command.execute(context=str(context)).return_code == 0
                lines = [l.rstrip() for l in o.getvalue().splitlines()]
                assert lines == ['hello', 'good-bye']

    def test_execute_with_context_and_cwd(self):
        with tempfile.TemporaryDirectory() as tmpd:
            context = pathlib.Path(tmpd)
            sub_dir = 'aa'
            context.joinpath(sub_dir).mkdir()
            for s in ['sample1', 'sample1.bat']:
                shutil.copy(
                    str(pathlib.Path(FILE_DIR, 'scripts', s)),
                    str(pathlib.Path(context, sub_dir, s)))

            with std_capture() as (o, e):
                command = Command('./sample1', cwd=sub_dir)
                assert command.execute(context=str(context)).return_code == 0
                lines = [l.rstrip() for l in o.getvalue().splitlines()]
                assert lines == ['hello', 'good-bye']

    def test_execute_absolute_cwd(self):
        with tempfile.TemporaryDirectory() as tmpd1, tempfile.TemporaryDirectory() as tmpd2:
            context = pathlib.Path(tmpd1)
            cwd = pathlib.Path(tmpd2, 'aa')
            cwd.mkdir()
            for s in ['sample1', 'sample1.bat']:
                shutil.copy(
                    str(pathlib.Path(FILE_DIR, 'scripts', s)),
                    str(pathlib.Path(cwd, s)))

            with std_capture() as (o, e):
                command = Command('./sample1', cwd=str(cwd))
                assert command.execute(context=str(context)).return_code == 0
                lines = [l.rstrip() for l in o.getvalue().splitlines()]
                assert lines == ['hello', 'good-bye']


@pytest.mark.skipif(platform.system() == 'Windows', reason='Not a Windows platform')
class TestForPosix:
    def test_new_command_by_relative_path(self):
        command = Command(['./dosome', '-a'])
        assert command.cmd == ['./dosome', '-a']
        assert str(command) == '[./dosome -a]'

    @pytest.mark.parametrize(
        'cmd_in, stdout', [
            (['echo', 'foo'], 'foo'),
            ('echo foo', 'foo'),
            ('echo "foo bar"', 'foo bar'),
        ])
    def test_execute_command(self, cmd_in, stdout):
        with std_capture() as (o, e):
            command = Command(cmd_in)
            assert command.execute().return_code == 0
            assert o.getvalue().rstrip() == stdout

    def test_execute_with_inputs(self):
        with std_capture() as (o, e):
            command = Command(['cat'])
            result = command.execute(inputs=['foo', 'bar'], timeout=3)
            assert result.return_code == 0
            assert len(result.stdout) == 2
            assert result.stdout[0].rstrip() == 'foo'
            assert result.stdout[1].rstrip() == 'bar'

            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['foo', 'bar']

    def test_execute_with_environment_variables(self):
        no_env = Command('./scripts/env_test', cwd=FILE_DIR)
        no_env_res = no_env.execute()

        assert no_env_res.return_code == 0
        assert no_env_res.stdout == ['']

        env = {'CERYLE_ENV_TEST': 'ceryle environment variable test'}
        with_env = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        with_env_res = with_env.execute()

        assert with_env_res.return_code == 0
        assert with_env_res.stdout == ['ceryle environment variable test']

    def test_execute_with_environment_variables_from_envs(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': 'ceryle environment variable test'})

        env = {'CERYLE_ENV_TEST': Env('FOO')}
        command = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['ceryle environment variable test']

    def test_execute_with_environment_variables_from_args(self, mocker):
        env = {'CERYLE_ENV_TEST': Arg('FOO', {'FOO': 'ceryle environment variable test'})}
        command = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['ceryle environment variable test']

    def test_with_envs_and_args(self, mocker):
        mocker.patch.dict('os.environ', {'ENV1': 'AAA'})
        args = {'ARG1': 'BBB'}
        command = Command(['echo', Env('ENV1'), Arg('ARG1', args)])
        res = command.execute()
        assert res.return_code == 0
        assert res.stdout == ['AAA BBB']

    def test_execute_command_containing_arg(self):
        arg = Arg('FOO', {'FOO': 'ceryle command arg test'})
        command = Command(['echo', arg])
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['ceryle command arg test']

    @pytest.mark.parametrize(
        'cwd', [
            Arg('TEST_CWD', {'TEST_CWD': str(FILE_DIR)}),
            PathArg(str(FILE_DIR)),
        ])
    def test_execute_with_cwd_by_arg(self, cwd):
        with_env = Command('./scripts/env_test', cwd=cwd)
        with_env_res = with_env.execute()

        assert with_env_res.return_code == 0
        assert with_env_res.stdout == ['']


@pytest.mark.skipif(platform.system() != 'Windows', reason='Not a Windows platform')
class TestForWin:
    @pytest.mark.parametrize(
        'cmd_in, cmd, cmd_str', [
            (['./dosome', '-a'], ['dosome', '-a'], '[dosome -a]'),
            ('./dosome -a', ['dosome', '-a'], '[dosome -a]'),
            (['./dir/dosome', '-a'], ['dir\\dosome', '-a'], '[dir\\dosome -a]'),
        ])
    def test_new_command_by_relative_path(self, cmd_in, cmd, cmd_str):
        command = Command(cmd)
        assert command.cmd == cmd
        assert str(command) == cmd_str

    @pytest.mark.parametrize(
        'cmd_in, stdout', [
            (['echo', 'foo'], 'foo'),
            ('echo foo', 'foo'),
            ('echo "foo bar"', '"foo bar"'),
        ])
    def test_execute_command(self, cmd_in, stdout):
        with std_capture() as (o, e):
            command = Command(cmd_in)
            assert command.execute().return_code == 0
            assert o.getvalue().rstrip() == stdout

    def test_execute_with_inputs(self):
        with std_capture() as (o, e):
            command = Command(['findstr', 'ba'])
            result = command.execute(inputs=['foo', 'bar', 'baz'], timeout=3)
            assert result.return_code == 0
            assert len(result.stdout) == 2
            assert result.stdout[0].rstrip() == 'bar'
            assert result.stdout[1].rstrip() == 'baz'

            lines = [l.rstrip() for l in o.getvalue().splitlines()]
            assert lines == ['bar', 'baz']

    def test_execute_with_environment_variables(self):
        no_env = Command('./scripts/env_test', cwd=FILE_DIR)
        no_env_res = no_env.execute()

        assert no_env_res.return_code == 0
        assert no_env_res.stdout == ['""']

        env = {'CERYLE_ENV_TEST': 'ceryle environment variable test'}
        with_env = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        with_env_res = with_env.execute()

        assert with_env_res.return_code == 0
        assert with_env_res.stdout == ['"ceryle environment variable test"']

    def test_execute_with_environment_variables_from_envs(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': 'ceryle environment variable test'})

        env = {'CERYLE_ENV_TEST': Env('FOO')}
        command = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['"ceryle environment variable test"']

    def test_execute_with_environment_variables_from_args(self, mocker):
        env = {'CERYLE_ENV_TEST': Arg('FOO', {'FOO': 'ceryle environment variable test'})}
        command = Command('./scripts/env_test', cwd=FILE_DIR, env=env)
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['"ceryle environment variable test"']

    def test_with_envs_and_args(self, mocker):
        mocker.patch.dict('os.environ', {'ENV1': 'AAA'})
        args = {'ARG1': 'BBB'}
        command = Command(['echo', Env('ENV1'), Arg('ARG1', args)])
        res = command.execute()
        assert res.return_code == 0
        assert res.stdout == ['AAA BBB']

    def test_execute_command_containing_arg(self):
        arg = Arg('FOO', {'FOO': 'ceryle command arg test'})
        command = Command(['echo', arg])
        res = command.execute()

        assert res.return_code == 0
        assert res.stdout == ['"ceryle command arg test"']

    @pytest.mark.parametrize(
        'cwd', [
            Arg('TEST_CWD', {'TEST_CWD': str(FILE_DIR)}),
            PathArg(str(FILE_DIR)),
        ])
    def test_execute_with_cwd_by_arg(self, cwd):
        with_env = Command('./scripts/env_test', cwd=cwd)
        with_env_res = with_env.execute()

        assert with_env_res.return_code == 0
        assert with_env_res.stdout == ['""']
