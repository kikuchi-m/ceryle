import os

from ceryle import ExecutionResult, TaskFileLoader, TaskGroup
from ceryle.commands.executable import ExecutableWrapper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def file_path(f):
    return os.path.join(SCRIPT_DIR, f)


def test_load_task_file():
    loader = TaskFileLoader(file_path('dsl_spec'))
    task_def = loader.load()

    assert task_def.default_task == 'foo'

    tasks = dict([(g.name, g) for g in task_def.tasks])
    task_names = tasks.keys()
    for name in ['foo', 'bar', 'simple', 'shorten', 'pipe', 'pipe2', 'args']:
        assert name in task_names
        assert isinstance(tasks[name], TaskGroup)


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
    assert 'my_cmd' in task_def.local_vars

    exe_res = foo.tasks[0].executable.execute()
    assert isinstance(exe_res, ExecutionResult)
    assert exe_res.return_code == 127


def test_load_task_file_no_task_def_contains_custome_executable():
    loader = TaskFileLoader(file_path('dsl_no_task_def_executable'))
    task_def = loader.load()

    assert len(task_def.tasks) == 0
    assert 'cmd_x' in task_def.local_vars
    assert 'cmd_y' in task_def.local_vars

    cmd_x = task_def.local_vars['cmd_x']()
    assert isinstance(cmd_x, ExecutableWrapper)

    cmd_x_res = cmd_x.execute()
    assert isinstance(cmd_x_res, ExecutionResult)
    assert cmd_x_res.return_code == 0
    assert cmd_x_res.stdout == ['cmd_x']

    cmd_y = task_def.local_vars['cmd_y']()
    assert isinstance(cmd_y, ExecutableWrapper)

    cmd_y_res = cmd_y.execute()
    assert isinstance(cmd_y_res, ExecutionResult)
    assert cmd_y_res.return_code == 0
    assert cmd_y_res.stdout == ['cmd_y']


def test_load_multiple():
    loader1 = TaskFileLoader(file_path('dsl_multiple1'))
    loader2 = TaskFileLoader(file_path('dsl_multiple2'))

    task_def1 = loader1.load()
    task_def2 = loader2.load(global_vars=task_def1.global_vars, local_vars=task_def1.local_vars)

    foo = task_def2.tasks[0]

    assert isinstance(foo, TaskGroup)
    assert foo.name == 'foo'
    assert len(foo.tasks) == 1
    assert isinstance(foo.tasks[0].executable, ExecutableWrapper)

    exe_res = foo.tasks[0].executable.execute()
    assert isinstance(exe_res, ExecutionResult)
    assert exe_res.return_code == 127

    assert 'my_cmd' in task_def2.local_vars
