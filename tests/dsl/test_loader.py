import os
import pytest

from ceryle import ExecutionResult, TaskGroup, TaskFileLoader, ExtensionLoader
from ceryle import TaskFileError
from ceryle.commands.executable import ExecutableWrapper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def file_path(f):
    return os.path.join(SCRIPT_DIR, f)


def test_load_task_file():
    p = file_path('dsl_spec')
    loader = TaskFileLoader(p)
    task_def = loader.load()

    assert task_def.default_task == 'foo'

    tasks = dict([(g.name, g) for g in task_def.tasks])
    task_names = tasks.keys()
    task_groups = [
        'foo', 'bar', 'simple', 'shorten',
        'pipe', 'pipe2',
        'task_attributes', 'task_group_attributes',
        'args',
    ]
    for name in task_groups:
        assert name in task_names
        g = tasks[name]
        assert isinstance(g, TaskGroup)
        assert g.filename == p


def test_load_task_file_no_task_def(mocker):
    test_file = file_path('dsl_no_task_def')
    loader = TaskFileLoader(test_file)
    with pytest.raises(TaskFileError) as e:
        loader.load()
    assert str(e.value) == f'No task definition found: {test_file}'


def test_load_task_file_not_dict(mocker):
    test_file = file_path('dsl_not_dict')
    loader = TaskFileLoader(test_file)
    with pytest.raises(TaskFileError) as e:
        loader.load()
    assert str(e.value) == f'Not task definition, declare by dict form: {test_file}'


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


def test_load_extension_file():
    loader = ExtensionLoader(file_path('dsl_no_task_def_executable'))
    extensions = loader.load()

    assert 'cmd_x' in extensions
    assert 'cmd_y' in extensions

    cmd_x = extensions['cmd_x']()
    assert isinstance(cmd_x, ExecutableWrapper)

    cmd_x_res = cmd_x.execute()
    assert isinstance(cmd_x_res, ExecutionResult)
    assert cmd_x_res.return_code == 0
    assert cmd_x_res.stdout == ['cmd_x']

    cmd_y = extensions['cmd_y']()
    assert isinstance(cmd_y, ExecutableWrapper)

    cmd_y_res = cmd_y.execute()
    assert isinstance(cmd_y_res, ExecutionResult)
    assert cmd_y_res.return_code == 0
    assert cmd_y_res.stdout == ['cmd_y']


def test_load_extension_multiple():
    loader1 = ExtensionLoader(file_path('dsl_multiple1'))
    loader2 = ExtensionLoader(file_path('dsl_multiple2'))

    ex1 = loader1.load()
    ex2 = loader2.load(local_vars=ex1)

    assert 'my_cmd1' in ex2
    assert 'my_cmd2' in ex2
