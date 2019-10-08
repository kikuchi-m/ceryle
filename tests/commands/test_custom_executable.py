import pytest

from ceryle import executable, Executable, ExecutionResult
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
