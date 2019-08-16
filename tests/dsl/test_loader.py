import os
import pytest

from ceryle import ExecutionResult, TaskFileLoader, TaskGroup
from ceryle.commands.executable import ExecutableWrapper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def file_path(f):
    return os.path.join(SCRIPT_DIR, f)


def test_load_task_file():
    loader = TaskFileLoader(file_path('dsl_spec'))
    task_def = loader.load()

    assert task_def.default_task == 'foo'

    task_groups = dict([(g.name, g) for g in task_def.tasks])
    assert len(task_groups) == 4

    foo = task_groups['foo']
    assert isinstance(foo, TaskGroup)
    assert foo.name == 'foo'

    bar = task_groups['bar']
    assert isinstance(bar, TaskGroup)
    assert bar.name == 'bar'

    simple = task_groups['simple']
    assert isinstance(simple, TaskGroup)
    assert simple.name == 'simple'

    shorten = task_groups['shorten']
    assert isinstance(shorten, TaskGroup)
    assert shorten.name == 'shorten'


def test_load_task_file_no_task_def(mocker):
    test_file = file_path('dsl_no_task_def')
    loader = TaskFileLoader(test_file)
    task_def = loader.load()
    assert len(task_def.tasks) == 0
    assert task_def.default_task is None


def test_load_task_file_not_dict(mocker):
    test_file = file_path('dsl_not_dict')
    loader = TaskFileLoader(test_file)
    task_def = loader.load()
    assert len(task_def.tasks) == 0
    assert task_def.default_task is None


def test_load_task_file_contains_custome_executable():
    loader = TaskFileLoader(file_path('dsl_executable'))
    task_def = loader.load()

    foo = task_def.tasks[0]

    assert isinstance(foo, TaskGroup)
    assert foo.name == 'foo'
    assert len(foo.tasks) == 1
    assert isinstance(foo.tasks[0].executable, ExecutableWrapper)

    exe_res = foo.tasks[0].executable.execute()
    assert isinstance(exe_res, ExecutionResult)
    assert exe_res.return_code == 127

    assert 'my_cmd' in task_def.local_vars
