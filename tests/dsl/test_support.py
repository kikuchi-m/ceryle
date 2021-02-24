import pathlib
import pytest

from ceryle import NoArgumentError, NoEnvironmentError
from ceryle.dsl.support import joinpath, ArgumentBase, Arg, Env, PathArg


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

    def test_eq_self(self):
        env = Env('FOO')

        assert env == env

    @pytest.mark.parametrize(
        'env1, env2, expected', [
            (Env('FOO'), Env('FOO'), True),
            (Env('FOO', allow_empty=True, default='dev', format='lib-%s.so'),
             Env('FOO', allow_empty=True, default='dev', format='lib-%s.so'),
             True),
            (Env('FOO', allow_empty=False), Env('FOO', allow_empty=True), False),
            (Env('FOO', default='dev'), Env('FOO', default='prod'), False),
            (Env('FOO', format='lib-%s.so'), Env('FOO', format='lib-%s.dll'), False),
            (Env('FOO'), None, False),
            (Env('FOO'), 'FOO', False),

            (Env('FOO') + 'X', Env('FOO') + 'X', True),
            ('X' + Env('FOO'), 'X' + Env('FOO'), True),
            (Env('FOO') + Env('X'), Env('FOO') + Env('X'), True),
            (Env('FOO') + Arg('X', {}), Env('FOO') + Arg('X', {}), True),
            (Env('FOO') + PathArg('X'), Env('FOO') + PathArg('X'), True),

            (Env('FOO'), Env('FOO') + 'X', False),
            (Env('FOO'), 'X' + Env('FOO'), False),
            (Env('FOO'), Env('FOO') + Env('X'), False),
            (Env('FOO'), Env('FOO') + Arg('X', {}), False),
            (Env('FOO'), Env('FOO') + PathArg('X'), False),
        ])
    def test_eq_other(self, env1, env2, expected):
        assert (env1 == env2) is expected
        assert (env2 == env1) is expected


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

    def test_eq_self(self):
        arg = Arg('FOO', {'FOO': 'xxx'})

        assert arg == arg

    @pytest.mark.parametrize(
        'arg1, arg2, expected', [
            (Arg('FOO', {}), Arg('FOO', {}), True),
            (Arg('FOO', {'FOO': 'xxx'}), Arg('FOO', {'FOO': 'xxx'}), True),
            (Arg('FOO', {'FOO': 'xxx'}, allow_empty=True, default='dev', format='lib-%s.so'),
             Arg('FOO', {'FOO': 'xxx'}, allow_empty=True, default='dev', format='lib-%s.so'),
             True),
            (Arg('FOO', {'FOO': 'x'}),
             Arg('FOO', {'BAR': 'x'}),
             False),
            (Arg('FOO', {'FOO': 'x'}),
             Arg('FOO', {'FOO': 'y'}),
             False),
            (Arg('FOO', {}, allow_empty=False),
             Arg('FOO', {}, allow_empty=True),
             False),
            (Arg('FOO', {}, default='dev'),
             Arg('FOO', {}, default='prod'),
             False),
            (Arg('FOO', {}, format='lib-%s.so'),
             Arg('FOO', {}, format='lib-%s.dll'),
             False),
            (Arg('FOO', {}), None, False),
            (Arg('FOO', {}), 'FOO', False),

            (Arg('FOO', {}) + 'X', Arg('FOO', {}) + 'X', True),
            ('X' + Arg('FOO', {}), 'X' + Arg('FOO', {}), True),
            (Arg('FOO', {}) + Arg('X', {}), Arg('FOO', {}) + Arg('X', {}), True),
            (Arg('FOO', {}) + Env('X'), Arg('FOO', {}) + Env('X'), True),
            (Arg('FOO', {}) + PathArg('X'), Arg('FOO', {}) + PathArg('X'), True),

            (Arg('FOO', {}), Arg('FOO', {}) + 'X', False),
            (Arg('FOO', {}), 'X' + Arg('FOO', {}), False),
            (Arg('FOO', {}), Arg('FOO', {}) + Arg('X', {}), False),
            (Arg('FOO', {}), Arg('FOO', {}) + Env('X'), False),
            (Arg('FOO', {}), Arg('FOO', {}) + PathArg('X'), False),
        ])
    def test_eq_other(self, arg1, arg2, expected):
        assert (arg1 == arg2) is expected
        assert (arg2 == arg1) is expected


def stub_arg(v):
    return Arg('A', {'A': v})


class TestPathArg:
    @pytest.mark.parametrize(
        'path, expected', [
            (('x',), pathlib.Path('x')),
            (('x', 'y'), pathlib.Path('x/y')),
            ((pathlib.Path('x'),), pathlib.Path('x')),
            (('x', pathlib.Path('y')), pathlib.Path('x/y')),
            ((pathlib.Path('x'), pathlib.Path('y')), pathlib.Path('x/y')),
            ((stub_arg('x'),), pathlib.Path('x')),
            (('a', stub_arg('x')), pathlib.Path('a', 'x')),
            ((stub_arg('x'), 'b'), pathlib.Path('x', 'b')),
            (('a', stub_arg('x'), 'b'), pathlib.Path('a', 'x', 'b')),
            ((stub_arg('x'), stub_arg('y')), pathlib.Path('x', 'y')),
            ((stub_arg('x'), 'a', stub_arg('y')), pathlib.Path('x', 'a', 'y')),
        ])
    def test_evaluate_returns_value(self, path, expected):
        assert PathArg(*path).evaluate() == str(expected)

    def test_combine_str_right(self):
        p_arg1 = PathArg('x', 'y')

        p_arg = p_arg1 + '.png'

        assert isinstance(p_arg, PathArg)
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == str(pathlib.Path('x', 'y.png'))

    def test_combine_str_left(self):
        p_arg1 = PathArg('x', 'y')

        p_arg = 'protocol:' + p_arg1

        assert isinstance(p_arg, PathArg)
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == 'protocol:' + str(pathlib.Path('x', 'y'))

    def test_combine_str_left_right(self):
        p_arg1 = PathArg('x', 'y')

        p_arg = 'protocol:' + p_arg1 + '.png'

        assert isinstance(p_arg, PathArg)
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == 'protocol:' + str(pathlib.Path('x', 'y.png'))

    def test_combine_arg_right(self):
        arg = Arg('FOO', {'FOO': '.png'})
        p_arg1 = PathArg('x', 'y')

        p_arg = p_arg1 + arg

        assert isinstance(p_arg, ArgumentBase)
        assert p_arg is not arg
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == str(pathlib.Path('x', 'y.png'))

    def test_combine_arg_left(self):
        arg = Arg('FOO', {'FOO': 'abc:'})
        p_arg1 = PathArg('x', 'y')

        p_arg = arg + p_arg1

        assert isinstance(p_arg, ArgumentBase)
        assert p_arg is not arg
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == 'abc:' + str(pathlib.Path('x', 'y'))

    def test_combine_arg_left_right(self):
        arg1 = Arg('FOO', {'FOO': 'abc:'})
        arg2 = Arg('BAR', {'BAR': '.png'})
        p_arg1 = PathArg('x', 'y')

        p_arg = arg1 + p_arg1 + arg2

        assert isinstance(p_arg, ArgumentBase)
        assert p_arg is not arg1
        assert p_arg is not arg2
        assert p_arg is not p_arg1
        assert p_arg.evaluate() == 'abc:' + str(pathlib.Path('x', 'y.png'))

    @pytest.mark.parametrize(
        'p_arg, expected', [
            (PathArg('x'), 'path(x)'),
            (PathArg('x', 'y'), 'path(x/y)'),
            (PathArg('x\\y'), 'path(x\\y)'),
            ('abc:' + PathArg('x', 'y'), "'abc:' + path(x/y)"),
            (PathArg('x', 'y') + '.png', "path(x/y) + '.png'"),
            (PathArg(stub_arg('v'), 'x'), f'path({stub_arg("v")}/x)'),
            (stub_arg('v') + PathArg('x', 'y'), f'{stub_arg("v")} + path(x/y)'),
        ])
    def test_str(self, p_arg, expected):
        assert str(p_arg) == expected


class TestJoinpath:
    def test_only_strs(self):
        p = joinpath('foo', 'bar')
        assert p.evaluate() == str(pathlib.Path('foo', 'bar'))

    @pytest.mark.parametrize(
        'path, expected', [
            ((stub_arg('x'),), pathlib.Path('x')),
            (('a', stub_arg('x')), pathlib.Path('a', 'x')),
            ((stub_arg('x'), 'b'), pathlib.Path('x', 'b')),
            (('a', stub_arg('x'), 'b'), pathlib.Path('a', 'x', 'b')),
            ((stub_arg('x'), stub_arg('y')), pathlib.Path('x', 'y')),
            ((stub_arg('x'), 'a', stub_arg('y')), pathlib.Path('x', 'a', 'y')),
        ])
    def test_with_arg(self, path, expected):
        p = joinpath(*path)

        assert isinstance(p, PathArg)
        assert p.evaluate() == str(expected)

    def test_eq_self(self):
        p = PathArg('a')

        assert p == p

    @pytest.mark.parametrize(
        'p1, p2, expected', [
            (PathArg('a'), PathArg('a'), True),
            (PathArg('a', 'b'), PathArg('a', 'b'), True),
            (PathArg('a'), PathArg('c'), False),
            (PathArg('a', 'b'), PathArg('a', 'c'), False),
            (PathArg('a'), None, False),
            (PathArg('a'), 'a', False),

            (PathArg('a') + 'X', PathArg('a') + 'X', True),
            ('X' + PathArg('a'), 'X' + PathArg('a'), True),
            (PathArg('a') + Arg('X', {}), PathArg('a') + Arg('X', {}), True),
            (PathArg('a') + Env('X'), PathArg('a') + Env('X'), True),
            (PathArg('a') + PathArg('x'), PathArg('a') + PathArg('x'), True),

            (PathArg('a'), PathArg('a') + 'X', False),
            (PathArg('a'), 'X' + PathArg('a'), False),
            (PathArg('a'), PathArg('a') + Env('X'), False),
            (PathArg('a'), PathArg('a') + Arg('X', {}), False),
            (PathArg('a'), PathArg('a') + PathArg('b'), False),
        ])
    def test_eq_other(self, p1, p2, expected):
        assert (p1 == p2) is expected
        assert (p2 == p1) is expected
