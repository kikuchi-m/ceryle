import pathlib
import pytest

import ceryle.dsl.support as support
from ceryle import NoEnvironmentError


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
