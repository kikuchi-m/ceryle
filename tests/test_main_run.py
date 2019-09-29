import ceryle
import ceryle.main
import pytest

from ceryle import TaskDefinitionError, TaskFileError


def test_main_run_default_task_group(mocker):
    util_mocks = mocker.Mock()
    dummy_extensions = [
        '/foo/home/.ceryle/extensions/x1.py',
        '/foo/bar/.ceryle/extensions/x2.py',
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)
    util_mocks.attach_mock(collect_ex_mock, 'collect_ex_mock')

    dummy_task_files = [
        '/foo/home/.ceryle/tasks/a.ceryle',
        '/foo/bar/CERYLE',
        '/foo/bar/.ceryle/tasks/b.ceryle',
    ]
    root_context = '/foo/bar'
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=(dummy_task_files, root_context))
    util_mocks.attach_mock(collect_tasks_mock, 'collect_tasks_mock')

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    util_expected_calls = [
        mocker.call.collect_tasks_mock(mocker.ANY),
        mocker.call.collect_ex_mock(mocker.ANY),
    ]
    assert util_mocks.mock_calls == util_expected_calls

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False)


def test_main_run_specific_task_group(mocker):
    dummy_extensions = [
        '/foo/home/.ceryle/extensions/x1.py',
        '/foo/bar/.ceryle/extensions/x2.py',
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        '/foo/home/.ceryle/tasks/a.ceryle',
        '/foo/bar/CERYLE',
        '/foo/bar/.ceryle/tasks/b.ceryle',
    ]
    root_context = '/foo/bar'
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=(dummy_task_files, root_context))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(task='tg2')

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg2', dry_run=False)


def test_main_run_fails_by_task_failure(mocker):
    dummy_extensions = [
        '/foo/home/.ceryle/extensions/x1.py',
        '/foo/bar/.ceryle/extensions/x2.py',
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        '/foo/home/.ceryle/tasks/a.ceryle',
        '/foo/bar/CERYLE',
        '/foo/bar/.ceryle/tasks/b.ceryle',
    ]
    root_context = '/foo/bar'
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=(dummy_task_files, root_context))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=False)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 1
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False)


def test_main_run_fails_by_task_file_not_found(mocker):
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=[])
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=([], None))

    with pytest.raises(TaskFileError) as e:
        ceryle.main.run()
    assert str(e.value) == 'task file not found'
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_not_called()


def test_main_run_raises_by_no_default_and_no_task_to_run(mocker):
    dummy_extensions = [
        '/foo/home/.ceryle/extensions/x1.py',
        '/foo/bar/.ceryle/extensions/x2.py',
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        '/foo/bar/CERYLE',
    ]
    root_context = '/foo/bar'
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=(dummy_task_files, root_context))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.default_task = None
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    # excercise
    with pytest.raises(TaskDefinitionError) as e:
        ceryle.main.run()
    assert str(e.value) == 'default task is not declared, specify task to run'
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})
