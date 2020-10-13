import pathlib
import pytest

from ceryle import NoArgumentError, NoEnvironmentError
from ceryle.dsl.support import joinpath, Arg, Env


def test_joinpath():
    assert joinpath('foo', 'bar') == str(pathlib.Path('foo', 'bar'))


class TestEnv:
    def test_evaluate_returns_value(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env = Env('FOO')
        assert env.evaluate() == '1'

    def test_evaluate_returns_default(self, mocker):
        mocker.patch.dict('os.environ', {})

        env = Env('FOO', default='-1')
        assert env.evaluate() == '-1'

    def test_evaluate_returns_empty(self, mocker):
        mocker.patch.dict('os.environ', {})

        env = Env('FOO', allow_empty=True)
        assert env.evaluate() == ''

    def test_evaluate_raises_if_absent(self, mocker):
        mocker.patch.dict('os.environ', {})

        env = Env('FOO')
        with pytest.raises(NoEnvironmentError) as e:
            env.evaluate()
        assert str(e.value) == 'environment variable FOO is not defined'

    def test_combine_right(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env1 = Env('FOO')
        env = env1 + '2'
        assert isinstance(env, Env)
        assert env1 is not env
        assert env.evaluate() == '12'

    def test_combine_left(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env1 = Env('FOO')
        env = '3' + env1
        assert isinstance(env, Env)
        assert env1 is not env
        assert env.evaluate() == '31'

    def test_combine_left_right(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env1 = Env('FOO')
        env = '3' + env1 + '2'
        assert isinstance(env, Env)
        assert env1 is not env
        assert env.evaluate() == '312'

    def test_combine_envs(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1', 'BAR': '0'})

        env1 = Env('FOO')
        env = env1 + Env('BAR')
        assert isinstance(env, Env)
        assert env1 is not env
        assert env.evaluate() == '10'

    def test_combine_self(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env1 = Env('FOO')
        env = env1 + env1
        assert isinstance(env, Env)
        assert env1 is not env
        assert env.evaluate() == '11'

    def test_combine_multiple(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1', 'BAR': '0'})

        env1 = '2' + Env('FOO') + '3'
        env2 = '4' + Env('BAR') + '5'
        env = env1 + env2
        assert isinstance(env, Env)
        assert env.evaluate() == '213405'

    def test_evaluate_with_formatting(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        env = Env('FOO', format='env: %(FOO)s')
        assert env.evaluate() == 'env: 1'

        env2 = Env('FOO', format='env: %(FOO)s') + ' count'
        assert env2.evaluate() == 'env: 1 count'

        env3 = 'env: ' + Env('FOO', format='%(FOO)s')
        assert env3.evaluate() == 'env: 1'

        env4 = Env('FOO') + Env('FOO', format=', %(FOO)s')
        assert env4.evaluate() == '1, 1'

    @pytest.mark.parametrize(
        'default, allow_empty, format, expected', [
            (None, False, None, 'env(FOO)'),
            ('x', False, None, 'env(FOO, default=x)'),
            (None, True, None, 'env(FOO, allow_empty)'),
            (None, False, 'option=%(FOO)s', 'env(FOO, format=\'option=%(FOO)s\')'),
            ('x', True, 'option=%(FOO)s', 'env(FOO, default=x, allow_empty, format=\'option=%(FOO)s\')'),
        ])
    def test_str(self, default, allow_empty, format, expected):
        env = Env('FOO', default=default, allow_empty=allow_empty, format=format)
        assert str(env) == expected

    def test_str_combined(self):
        env1 = '2' + Env('FOO') + '3'
        env2 = '4' + Env('BAR') + '5'
        env = env1 + env2
        assert isinstance(env, Env)
        assert str(env) == "'2' + env(FOO) + '3' + '4' + env(BAR) + '5'"


class TestArg:
    def test_evaluate_returns_value(self):
        arg = Arg('FOO', {'FOO': '1'})
        assert arg.evaluate() == '1'

    def test_evaluate_returns_default(self):
        arg = Arg('FOO', {}, default='-1')
        assert arg.evaluate() == '-1'

    def test_evaluate_returns_empty(self):
        arg = Arg('FOO', {}, allow_empty=True)
        assert arg.evaluate() == ''

    def test_in_environment_variables(self, mocker):
        mocker.patch.dict('os.environ', {'FOO': '1'})

        arg = Arg('FOO', {})
        assert arg.evaluate() == '1'

        arg = Arg('FOO', {'FOO': '2'})
        assert arg.evaluate() == '2'

    def test_evaluate_raises_if_absent(self):
        arg = Arg('FOO', {})
        with pytest.raises(NoArgumentError) as e:
            arg.evaluate()
        assert str(e.value) == 'argument FOO is not defined'

    def test_combine_right(self):
        args = {'FOO': '1'}

        arg1 = Arg('FOO', args)
        arg = arg1 + '2'
        assert isinstance(arg, Arg)
        assert arg1 is not arg
        assert arg.evaluate() == '12'

    def test_combine_left(self):
        args = {'FOO': '1'}

        arg1 = Arg('FOO', args)
        arg = '3' + arg1
        assert isinstance(arg, Arg)
        assert arg1 is not arg
        assert arg.evaluate() == '31'

    def test_combine_left_right(self):
        args = {'FOO': '1'}

        arg1 = Arg('FOO', args)
        arg = '3' + arg1 + '2'
        assert isinstance(arg, Arg)
        assert arg1 is not arg
        assert arg.evaluate() == '312'

    def test_combine_args(self):
        args = {'FOO': '1', 'BAR': '0'}

        arg1 = Arg('FOO', args)
        arg = arg1 + Arg('BAR', args)
        assert isinstance(arg, Arg)
        assert arg1 is not arg
        assert arg.evaluate() == '10'

    def test_combine_self(self):
        args = {'FOO': '1'}

        arg1 = Arg('FOO', args)
        arg = arg1 + arg1
        assert isinstance(arg, Arg)
        assert arg1 is not arg
        assert arg.evaluate() == '11'

    def test_combine_multiple(self):
        args = {'FOO': '1', 'BAR': '0'}

        arg1 = '2' + Arg('FOO', args) + '3'
        arg2 = '4' + Arg('BAR', args) + '5'
        arg = arg1 + arg2
        assert isinstance(arg, Arg)
        assert arg.evaluate() == '213405'

    def test_evaluate_with_formatting(self):
        args = {'FOO': '1'}

        arg1 = Arg('FOO', args, format='arg: %(FOO)s')
        assert arg1.evaluate() == 'arg: 1'

        arg2 = Arg('FOO', args, format='arg: %(FOO)s') + ' count'
        assert arg2.evaluate() == 'arg: 1 count'

        arg3 = 'arg: ' + Arg('FOO', args, format='%(FOO)s')
        assert arg3.evaluate() == 'arg: 1'

        arg4 = Arg('FOO', args) + Arg('FOO', args, format=', %(FOO)s')
        assert arg4.evaluate() == '1, 1'

    @pytest.mark.parametrize(
        'default, allow_empty, format, expected', [
            (None, False, None, 'arg(FOO)'),
            ('x', False, None, 'arg(FOO, default=x)'),
            (None, True, None, 'arg(FOO, allow_empty)'),
            (None, False, 'option=%(FOO)s', 'arg(FOO, format=\'option=%(FOO)s\')'),
            ('x', True, 'option=%(FOO)s', 'arg(FOO, default=x, allow_empty, format=\'option=%(FOO)s\')'),
        ])
    def test_str(self, default, allow_empty, format, expected):
        arg = Arg('FOO', {}, default=default, allow_empty=allow_empty, format=format)
        assert str(arg) == expected

    def test_str_combined(self):
        args = {'FOO': '1', 'BAR': '0'}

        arg1 = '2' + Arg('FOO', args) + '3'
        arg2 = '4' + Arg('BAR', args) + '5'
        arg = arg1 + arg2
        assert isinstance(arg, Arg)
        assert str(arg) == "'2' + arg(FOO) + '3' + '4' + arg(BAR) + '5'"
