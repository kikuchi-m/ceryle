import pathlib
import pytest

import ceryle.dsl.support as support
from ceryle import NoArgumentError, NoEnvironmentError


def test_joinpath():
    assert support.joinpath('foo', 'bar') == str(pathlib.Path('foo', 'bar'))


def test_env_evaluate_returns_value(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env = support.Env('FOO')
    assert env.evaluate() == '1'


def test_env_evaluate_returns_default(mocker):
    mocker.patch.dict('os.environ', {})

    env = support.Env('FOO', default='-1')
    assert env.evaluate() == '-1'


def test_env_evaluate_returns_empty(mocker):
    mocker.patch.dict('os.environ', {})

    env = support.Env('FOO', allow_empty=True)
    assert env.evaluate() == ''


def test_env_evaluate_raises_if_absent(mocker):
    mocker.patch.dict('os.environ', {})

    env = support.Env('FOO')
    with pytest.raises(NoEnvironmentError) as e:
        env.evaluate()
    assert str(e.value) == 'environment variable FOO is not defined'


def test_env_combine_right(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env1 = support.Env('FOO')
    env = env1 + '2'
    assert isinstance(env, support.Env)
    assert env1 is not env
    assert env.evaluate() == '12'


def test_env_combine_left(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env1 = support.Env('FOO')
    env = '3' + env1
    assert isinstance(env, support.Env)
    assert env1 is not env
    assert env.evaluate() == '31'


def test_env_combine_left_right(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env1 = support.Env('FOO')
    env = '3' + env1 + '2'
    assert isinstance(env, support.Env)
    assert env1 is not env
    assert env.evaluate() == '312'


def test_env_combine_envs(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1', 'BAR': '0'})

    env1 = support.Env('FOO')
    env = env1 + support.Env('BAR')
    assert isinstance(env, support.Env)
    assert env1 is not env
    assert env.evaluate() == '10'


def test_env_combine_self(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env1 = support.Env('FOO')
    env = env1 + env1
    assert isinstance(env, support.Env)
    assert env1 is not env
    assert env.evaluate() == '11'


def test_env_combine_multiple(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1', 'BAR': '0'})

    env1 = '2' + support.Env('FOO') + '3'
    env2 = '4' + support.Env('BAR') + '5'
    env = env1 + env2
    assert isinstance(env, support.Env)
    assert env.evaluate() == '213405'


def test_env_format(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env = support.Env('FOO', format='env: %(FOO)s')
    assert env.evaluate() == 'env: 1'

    env2 = support.Env('FOO', format='env: %(FOO)s') + ' count'
    assert env2.evaluate() == 'env: 1 count'

    env3 = 'env: ' + support.Env('FOO', format='%(FOO)s')
    assert env3.evaluate() == 'env: 1'

    env4 = support.Env('FOO') + support.Env('FOO', format=', %(FOO)s')
    assert env4.evaluate() == '1, 1'


@pytest.mark.parametrize(
    'default, allow_empty, format, expected', [
        (None, False, None, 'env(FOO)'),
        ('x', False, None, 'env(FOO, default=x)'),
        (None, True, None, 'env(FOO, allow_empty)'),
        (None, False, 'option=%(FOO)s', 'env(FOO, format=\'option=%(FOO)s\')'),
        ('x', True, 'option=%(FOO)s', 'env(FOO, default=x, allow_empty, format=\'option=%(FOO)s\')'),
    ])
def test_env_str(default, allow_empty, format, expected):
    env = support.Env('FOO', default=default, allow_empty=allow_empty, format=format)
    assert str(env) == expected


def test_env_str_combined():
    env1 = '2' + support.Env('FOO') + '3'
    env2 = '4' + support.Env('BAR') + '5'
    env = env1 + env2
    assert isinstance(env, support.Env)
    assert str(env) == "'2' + env(FOO) + '3' + '4' + env(BAR) + '5'"


def test_arg_evaluate_returns_value():
    arg = support.Arg('FOO', {'FOO': '1'})
    assert arg.evaluate() == '1'


def test_arg_evaluate_returns_default():
    arg = support.Arg('FOO', {}, default='-1')
    assert arg.evaluate() == '-1'


def test_arg_evaluate_returns_empty():
    arg = support.Arg('FOO', {}, allow_empty=True)
    assert arg.evaluate() == ''


def test_arg_in_environment_variables(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    arg = support.Arg('FOO', {})
    assert arg.evaluate() == '1'

    arg = support.Arg('FOO', {'FOO': '2'})
    assert arg.evaluate() == '2'


def test_arg_evaluate_raises_if_absent():
    arg = support.Arg('FOO', {})
    with pytest.raises(NoArgumentError) as e:
        arg.evaluate()
    assert str(e.value) == 'argument FOO is not defined'


def test_arg_combine_right():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args)
    arg = arg1 + '2'
    assert isinstance(arg, support.Arg)
    assert arg1 is not arg
    assert arg.evaluate() == '12'


def test_arg_combine_left():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args)
    arg = '3' + arg1
    assert isinstance(arg, support.Arg)
    assert arg1 is not arg
    assert arg.evaluate() == '31'


def test_arg_combine_left_right():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args)
    arg = '3' + arg1 + '2'
    assert isinstance(arg, support.Arg)
    assert arg1 is not arg
    assert arg.evaluate() == '312'


def test_arg_combine_args():
    args = {'FOO': '1', 'BAR': '0'}

    arg1 = support.Arg('FOO', args)
    arg = arg1 + support.Arg('BAR', args)
    assert isinstance(arg, support.Arg)
    assert arg1 is not arg
    assert arg.evaluate() == '10'


def test_arg_combine_self():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args)
    arg = arg1 + arg1
    assert isinstance(arg, support.Arg)
    assert arg1 is not arg
    assert arg.evaluate() == '11'


def test_arg_combine_multiple():
    args = {'FOO': '1', 'BAR': '0'}

    arg1 = '2' + support.Arg('FOO', args) + '3'
    arg2 = '4' + support.Arg('BAR', args) + '5'
    arg = arg1 + arg2
    assert isinstance(arg, support.Arg)
    assert arg.evaluate() == '213405'


def test_arg_format():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args, format='arg: %(FOO)s')
    assert arg1.evaluate() == 'arg: 1'

    arg2 = support.Arg('FOO', args, format='arg: %(FOO)s') + ' count'
    assert arg2.evaluate() == 'arg: 1 count'

    arg3 = 'arg: ' + support.Arg('FOO', args, format='%(FOO)s')
    assert arg3.evaluate() == 'arg: 1'

    arg4 = support.Arg('FOO', args) + support.Arg('FOO', args, format=', %(FOO)s')
    assert arg4.evaluate() == '1, 1'


@pytest.mark.parametrize(
    'default, allow_empty, format, expected', [
        (None, False, None, 'arg(FOO)'),
        ('x', False, None, 'arg(FOO, default=x)'),
        (None, True, None, 'arg(FOO, allow_empty)'),
        (None, False, 'option=%(FOO)s', 'arg(FOO, format=\'option=%(FOO)s\')'),
        ('x', True, 'option=%(FOO)s', 'arg(FOO, default=x, allow_empty, format=\'option=%(FOO)s\')'),
    ])
def test_arg_str(default, allow_empty, format, expected):
    arg = support.Arg('FOO', {}, default=default, allow_empty=allow_empty, format=format)
    assert str(arg) == expected


def test_arg_str_combined():
    args = {'FOO': '1', 'BAR': '0'}

    arg1 = '2' + support.Arg('FOO', args) + '3'
    arg2 = '4' + support.Arg('BAR', args) + '5'
    arg = arg1 + arg2
    assert isinstance(arg, support.Arg)
    assert str(arg) == "'2' + arg(FOO) + '3' + '4' + arg(BAR) + '5'"
