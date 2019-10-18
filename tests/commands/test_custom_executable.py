import pytest

from ceryle import executable, executable_with, Executable, ExecutionResult
from ceryle.dsl.support import Env, Arg


def test_custom_executable():
    @executable
    def mycommand():
        return ExecutionResult(0)

    myexe = mycommand()
    assert isinstance(myexe, Executable)

    res = myexe.execute()
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0


def test_custom_executable_str():
    @executable
    def exe1():
        return ExecutionResult(0)

    assert str(exe1()) == 'exe1()'

    @executable
    def exe2(a, b):
        return ExecutionResult(0)

    assert str(exe2(1, 'foo')) == 'exe2(1, foo)'

    @executable
    def exe3(a, b=False):
        return ExecutionResult(0)

    assert str(exe3(1, b=True)) == 'exe3(1, b=True)'

    @executable
    def exe4(a):
        return ExecutionResult(0)

    assert str(exe4(Env('FOO'))) == 'exe4(env(FOO))'

    @executable_with(name='foo')
    def exe5(a):
        return ExecutionResult(0)

    assert str(exe5(1)) == 'foo(1)'


def test_custom_executable_returns_int():
    @executable
    def mycommand():
        return 127

    res = mycommand().execute()
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 127


@pytest.mark.parametrize(
    'ret,return_code',
    [(True, 0), (False, 1)])
def test_custom_executable_returns_bool(ret, return_code):
    @executable
    def mycommand():
        return ret

    res = mycommand().execute()
    assert isinstance(res, ExecutionResult)
    assert res.return_code == return_code


def test_custom_executable_returns_none_object():
    @executable
    def mycommand():
        pass

    res = mycommand().execute()
    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0


def test_raises_when_returning_incorrect_object():
    @executable
    def mycommand():
        return 'foo'

    with pytest.raises(RuntimeError) as e:
        mycommand().execute()
    assert str(e.value) == 'ExecutionResult was not returned by mycommand'


def test_no_args():
    @executable
    def mycommand():
        return ExecutionResult(0)

    res = mycommand().execute(context='execution_context')
    assert res.return_code == 0


def test_positional_args():
    @executable
    def mycommand(a):
        if a == 10:
            return ExecutionResult(0)
        return ExecutionResult(255)

    res1 = mycommand(10).execute(context='execution_context')
    assert res1.return_code == 0

    res2 = mycommand(11).execute(context='execution_context')
    assert res2.return_code == 255


def test_kwargs():
    @executable
    def mycommand(myarg=0):
        return ExecutionResult(myarg)

    res1 = mycommand().execute(context='execution_context')
    assert res1.return_code == 0

    res2 = mycommand(myarg=2).execute(context='execution_context')
    assert res2.return_code == 2


def test_reserved_kwargs():
    @executable
    def mycommand(myarg=0, context=None):
        if myarg == 1 and context == 'execution_context':
            return ExecutionResult(0)
        return ExecutionResult(255)

    res1 = mycommand(myarg=1).execute(context='execution_context')
    assert res1.return_code == 0

    res2 = mycommand(myarg=1).execute(context='another_context')
    assert res2.return_code == 255


def test_positional_and_kwargs():
    @executable
    def mycommand(parg, myarg=0):
        if parg == 1 and myarg == 2:
            return ExecutionResult(0)
        return ExecutionResult(255)

    res1 = mycommand(1, myarg=2).execute(context='execution_context')
    assert res1.return_code == 0

    res2 = mycommand(1).execute(context='execution_context')
    assert res2.return_code == 255

    @executable
    def mycommand2(parg, myarg=0, context=None):
        if parg == 1 and myarg == 2 and context == 'execution_context':
            return ExecutionResult(0)
        return ExecutionResult(255)

    res3 = mycommand2(1, myarg=2).execute(context='execution_context')
    assert res3.return_code == 0

    res4 = mycommand2(1, myarg=2).execute(context='another_context')
    assert res4.return_code == 255


def test_varargs_posx():
    @executable
    def mycommand(*args):
        assert args == (1, 2, 3, 4)
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4)
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_pos_posx():
    @executable
    def mycommand(a, b, *args):
        assert a == 1 and b == 2
        assert args == (3, 4)
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4)
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_pos_posx_kw():
    @executable
    def mycommand(a, b, *args, x=0.1, y=False, z=None):
        assert a == 1 and b == 2
        assert x == 0.1
        assert y is True
        assert z is None
        return ExecutionResult(0)

    exe = mycommand(1, 2, y=True, kw1='foo')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_kwx():
    @executable
    def mycommand(**kwargs):
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(kw1='foo')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_kw_kwx():
    @executable
    def mycommand(x=0.1, y=False, z=None, **kwargs):
        assert x == 0.1
        assert y is True
        assert z is None
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(y=True, kw1='foo')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_kw_kwx2():
    @executable
    def mycommand(x=None, **kwargs):
        assert x is None
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(kw1='foo', context='dummy')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_pos_kwx():
    @executable
    def mycommand(a, b, **kwargs):
        assert a == 1 and b == 2
        assert kwargs == dict(
            kw1='foo',
            y=True,
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(1, 2, y=True, kw1='foo')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_posx_kwx():
    @executable
    def mycommand(*args, **kwargs):
        assert args == (1, 2, 3, 4)
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4, kw1='foo', context='dummy')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_pos_posx_kwx():
    @executable
    def mycommand(a, b, *args, **kwargs):
        assert a == 1 and b == 2
        assert args == (3, 4)
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4, kw1='foo', context='dummy')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_posx_kw_kwx():
    @executable
    def mycommand(*args, x=0.1, y=False, z=None, **kwargs):
        assert args == (1, 2, 3, 4)
        assert x == 0.1
        assert y is True
        assert z is None
        assert kwargs == dict(
            kw1='foo',
            context='execution_context')
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4, y=True, kw1='foo', context='dummy')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_varargs_pos_posx_kw_kwx():
    @executable
    def mycommand(a, b, *args, x=0.1, y=False, context=None, **kwargs):
        assert a == 1 and b == 2
        assert args == (3, 4)
        assert x == 0.1
        assert y is True
        assert context == 'execution_context'
        assert kwargs == dict(kw1='foo')
        return ExecutionResult(0)

    exe = mycommand(1, 2, 3, 4, y=True, kw1='foo', context='dummy')
    res = exe.execute(context='execution_context')
    assert res.return_code == 0


def test_envs_and_additional_args(mocker):
    @executable
    def mycommand(parg1, parg2, kwarg1=None, kwarg2=None):
        return ExecutionResult(0, stdout=[parg1, parg2, kwarg1, kwarg2])

    mocker.patch.dict('os.environ', {'ENV1': 'AAA', 'ENV2': 'BBB'})
    args = {
        'ARG1': 'CCC',
        'ARG2': 'DDD',
    }
    res = mycommand(Env('ENV1'), Arg('ARG1', args), kwarg1=Env('ENV2'), kwarg2=Arg('ARG2', args)).execute()

    assert res.return_code == 0
    assert res.stdout == ['AAA', 'CCC', 'BBB', 'DDD']
