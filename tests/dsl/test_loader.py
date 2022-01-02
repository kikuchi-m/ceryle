import os
import pathlib

import pytest

from ceryle import Command, TaskFileLoader, ExtensionLoader
from ceryle import TaskFileError
from ceryle.commands.executable import ExecutableWrapper
from ceryle.tasks.condition import Condition
from ceryle.tasks.task import CommandInput, SingleValueCommandInput, MultiCommandInput
from ceryle.dsl.support import Arg, Env, PathArg

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTEXT = pathlib.Path(SCRIPT_DIR, 'spec')


def spec_file(name):
    return CONTEXT / name


class DSLSpecBase:
    def load(self, name, context=None):
        return TaskFileLoader(spec_file(name), context or CONTEXT).load()


class TestTaskGroupSpec(DSLSpecBase):
    def test_dependency(self):
        task_def = self.load('test_dependency.ceryle')

        assert len(task_def.tasks) == 3

        tg1 = task_def.find_task_group('group1')
        assert tg1.dependencies == ['group2', 'group3']

    def test_disable_skip_duplicate_dependency(self):
        task_def = self.load('test_disable_skip_duplicate_dependency.ceryle')

        tg2 = task_def.find_task_group('group2')
        assert tg2.allow_skip is False


class TestTaskSpec(DSLSpecBase):
    def test_tasks(self):
        task_def = self.load('test_tasks.ceryle')

        tg = task_def.find_task_group('test-tasks')
        assert tg is not None
        assert len(tg.tasks) == 2

    def test_simple_tasks(self):
        task_def = self.load('test_simple_tasks.ceryle')

        tg = task_def.find_task_group('test-tasks')
        assert tg is not None
        assert len(tg.tasks) == 2

    def test_tasks_only(self):
        task_def = self.load('test_tasks_only.ceryle')

        tg = task_def.find_task_group('test-tasks')
        assert tg is not None
        assert len(tg.tasks) == 2

    def test_pipe_in_same_group(self):
        task_def = self.load('test_pipe_in_same_group.ceryle')

        pipe = task_def.find_task_group('pipe')
        assert pipe.tasks[0].stdout_key == 'PIPE_OUTPUT'
        assert pipe.tasks[1].command_input == CommandInput('PIPE_OUTPUT')

    def test_pipe_with_group(self):
        task_def = self.load('test_pipe_with_group.ceryle')

        pipe = task_def.find_task_group('pipe')
        assert pipe.tasks[1].command_input == CommandInput('pipe', 'PIPE_OUTPUT')

    def test_pipe_as_single_value(self):
        task_def = self.load('test_pipe_as_single_value.ceryle')

        pipe = task_def.find_task_group('pipe')
        assert pipe.tasks[1].command_input == SingleValueCommandInput('PIPE_OUTPUT')

    def test_pipe_multiple_inputs(self):
        task_def = self.load('test_pipe_multiple_inputs.ceryle')

        pipe = task_def.find_task_group('pipe')
        assert pipe.tasks[2].command_input == MultiCommandInput('PIPE_OUTPUT1', ('pipe', 'PIPE_OUTPUT2'))

    def test_ignore_failure(self):
        task_def = self.load('test_ignore_failure.ceryle')

        task = task_def.find_task_group('test-task')
        assert task.tasks[0].ignore_failure is True

    @pytest.mark.parametrize(
        'ceryle_file', [
            'test_condition_command.ceryle',
            'test_condition_has_input.ceryle',
            'test_condition_no_input.ceryle',
            'test_condition_fail.ceryle',
            'test_condition_expression.ceryle',
            'test_condition_win.ceryle',
            'test_condition_mac.ceryle',
            'test_condition_linux.ceryle',
            'test_condition_all.ceryle',
            'test_condition_any.ceryle',
            'test_condition_bool_true.ceryle',
            'test_condition_bool_false.ceryle',
        ])
    def test_conditions(self, ceryle_file):
        task_def = self.load(ceryle_file)

        task = task_def.find_task_group('conditional-task')
        assert isinstance(task.tasks[0].condition, Condition)


class TestExecutableSpec(DSLSpecBase):
    def test_command(self):
        task_def = self.load('test_command.ceryle')

        tg = task_def.find_task_group('test-command')

        assert isinstance(tg.tasks[0].executable, Command)
        assert tg.tasks[0].executable.cmd == ['echo', 'a', 'b']

        assert isinstance(tg.tasks[1].executable, Command)
        assert tg.tasks[1].executable.cmd == ['echo', 'a', 'b']

    def test_command_options(self):
        task_def = self.load('test_command_options.ceryle')

        tg = task_def.find_task_group('test-command')

        assert tg.tasks[0].executable.cmd == ['echo', 'a', 'b']
        assert tg.tasks[0].executable.cwd is None
        assert tg.tasks[0].executable.inputs_as_args is False
        assert tg.tasks[0].executable.quiet is False
        assert tg.tasks[0].executable.env == {}

        assert tg.tasks[1].executable.cmd == ['echo', 'a', 'b']
        assert tg.tasks[1].executable.cwd == './x/y'
        assert tg.tasks[1].executable.inputs_as_args is True
        assert tg.tasks[1].executable.quiet is True
        assert tg.tasks[1].executable.env == {'MY_ENV': 'foo'}

    def test_command_with_arg(self):
        task_def = self.load('test_command_with_arg.ceryle')

        tg = task_def.find_task_group('test-command')

        assert tg.tasks[0].executable.cmd == ['my.sh', Arg('X1', {})]
        assert tg.tasks[1].executable.cmd == ['my.sh', Arg('X2', {}, allow_empty=True)]
        assert tg.tasks[2].executable.cmd == ['my.sh', Arg('X3', {}, default='Y3', format='X3=%(X3)s')]

    def test_command_with_env(self):
        task_def = self.load('test_command_with_env.ceryle')

        tg = task_def.find_task_group('test-command')

        assert tg.tasks[0].executable.cmd == ['my.sh', Env('E1')]
        assert tg.tasks[1].executable.cmd == ['my.sh', Env('E2', allow_empty=True)]
        assert tg.tasks[2].executable.cmd == ['my.sh', Env('E3', default='XX', format='E3=%(E3)s')]

    def test_command_with_patharg(self):
        task_def = self.load('test_command_with_patharg.ceryle')

        tg = task_def.find_task_group('test-command')

        assert tg.tasks[0].executable.cmd == ['my.sh', PathArg('a', 'b')]

    def test_custom_executable(self):
        task_def = self.load('test_custom_executable.ceryle')

        tg = task_def.find_task_group('test-task')

        assert len(tg.tasks) == 1
        assert isinstance(tg.tasks[0].executable, ExecutableWrapper)

    def test_mkdir(self):
        self.load('test_mkdir.ceryle')

    def test_copy(self):
        self.load('test_copy.ceryle')

    def test_module_var(self):
        task_def = self.load('test_module_var.ceryle')

        tg = task_def.find_task_group('mod_vars')

        assert tg.tasks[0].executable.cmd == ['echo', 'a', 'b']

    def test_module_var_list_comprehension(self):
        task_def = self.load('test_module_var_list_comprehension.ceryle')

        tg = task_def.find_task_group('mod_vars')

        assert tg.tasks[0].executable.cmd == ['echo', '1', '2', '3']

    def test_module_var_list_comprehension_tasks(self):
        task_def = self.load('test_module_var_list_comprehension_tasks.ceryle')

        tg = task_def.find_task_group('mod_vars')

        assert len(tg.tasks) == 3
        assert tg.tasks[0].executable.cmd == ['echo', '1']
        assert tg.tasks[1].executable.cmd == ['echo', '2']
        assert tg.tasks[2].executable.cmd == ['echo', '3']


class TestTaskFileSpec(DSLSpecBase):
    def test_with_context(self):
        task_def = self.load('test_with_context.ceryle', context=CONTEXT)

        tg = task_def.find_task_group('test-task')

        assert tg.context == CONTEXT / 'foo' / 'bar'

    def test_no_task_def(self):
        with pytest.raises(TaskFileError) as e:
            self.load('test_no_task_def.ceryle')

        task_file = spec_file('test_no_task_def.ceryle')
        assert str(e.value) == f'No task definition found: {task_file}'

    def test_not_dict(self):
        with pytest.raises(TaskFileError) as e:
            self.load('test_not_dict.ceryle')

        task_file = spec_file('test_not_dict.ceryle')
        assert str(e.value) == f'Not task definition, declare by dict form: {task_file}'


class TestExtensionFileSpec:
    def load(self, name, local_vars={}):
        return ExtensionLoader(spec_file(name)).load(local_vars=local_vars)

    def test_extensions(self):
        extensions = self.load('test_extensions.ceryle')

        assert 'extension1' in extensions

        extension1 = extensions['extension1']()
        assert isinstance(extension1, ExecutableWrapper)

        assert 'extension2' in extensions

        extension2 = extensions['extension2'](1)
        assert isinstance(extension2, ExecutableWrapper)

    def test_load_extension_with_local_vars(self):
        lvars = {
            'pre_defined_var': 1,
        }

        extensions = self.load('test_extensions.ceryle', local_vars=lvars)

        assert 'pre_defined_var' in extensions
        assert extensions['pre_defined_var'] == 1
