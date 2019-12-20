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


def test_env_combine(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1', 'BAR': '0'})

    env1 = support.Env('FOO')
    env2 = env1 + '2'
    assert isinstance(env2, support.Env)
    assert env1 is not env2
    assert env2.evaluate() == '12'

    env3 = '3' + env1
    assert isinstance(env3, support.Env)
    assert env1 is not env3
    assert env3.evaluate() == '31'

    env4 = env1 + support.Env('BAR')
    assert isinstance(env4, support.Env)
    assert env1 is not env4
    assert env4.evaluate() == '10'

    env5 = support.Env('BAR') + env1
    assert isinstance(env5, support.Env)
    assert env1 is not env5
    assert env5.evaluate() == '01'

    env6 = env1 + env1
    assert isinstance(env6, support.Env)
    assert env1 is not env6
    assert env6.evaluate() == '11'


def test_env_format(mocker):
    mocker.patch.dict('os.environ', {'FOO': '1'})

    env = support.Env('FOO', format='env: %(FOO)s')
    assert env.evaluate() == 'env: 1'


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


def test_arg_combine():
    args = {'FOO': '1', 'BAR': '0'}

    arg1 = support.Arg('FOO', args)
    arg2 = arg1 + '2'
    assert isinstance(arg2, support.Arg)
    assert arg1 is not arg2
    assert arg2.evaluate() == '12'

    arg3 = '3' + arg1
    assert isinstance(arg3, support.Arg)
    assert arg1 is not arg3
    assert arg3.evaluate() == '31'

    arg4 = arg1 + support.Arg('BAR', args)
    assert isinstance(arg4, support.Arg)
    assert arg1 is not arg4
    assert arg4.evaluate() == '10'

    arg5 = support.Arg('BAR', args) + arg1
    assert isinstance(arg5, support.Arg)
    assert arg1 is not arg5
    assert arg5.evaluate() == '01'

    arg6 = arg1 + arg1
    assert isinstance(arg6, support.Arg)
    assert arg1 is not arg6
    assert arg6.evaluate() == '11'


def test_arg_format():
    args = {'FOO': '1'}

    arg1 = support.Arg('FOO', args, format='arg: %(FOO)s')
    assert arg1.evaluate() == 'arg: 1'
