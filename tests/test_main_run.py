import ceryle
import ceryle.main
import pytest

from ceryle import TaskDefinitionError, TaskFileError


def test_main_run_default_task_group(mocker):
    dummy_task_file = '/foo/bar/CERYLE_TASKS'
    find_mock = mocker.patch('ceryle.util.find_task_file', return_value=dummy_task_file)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.context = '/foo/bar'
    task_def.default_task = 'tg1'

    loader = ceryle.TaskFileLoader(dummy_task_file)
    loader.load = mocker.Mock(return_value=task_def)
    loader_cls = mocker.patch('ceryle.TaskFileLoader', return_value=loader)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 0
    find_mock.assert_called_once_with(mocker.ANY)

    loader_cls.assert_called_once_with(dummy_task_file)
    loader.load.assert_called_once_with()

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1')


def test_main_run_task_group(mocker):
    dummy_task_file = '/foo/bar/CERYLE_TASKS'
    find_mock = mocker.patch('ceryle.util.find_task_file', return_value=dummy_task_file)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.context = '/foo/bar'
    task_def.default_task = 'tg1'

    loader = ceryle.TaskFileLoader(dummy_task_file)
    loader.load = mocker.Mock(return_value=task_def)
    loader_cls = mocker.patch('ceryle.TaskFileLoader', return_value=loader)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(task='tg2')

    # verification
    assert res == 0
    find_mock.assert_called_once_with(mocker.ANY)

    loader_cls.assert_called_once_with(dummy_task_file)
    loader.load.assert_called_once_with()

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg2')


def test_main_run_fails_by_task_failure(mocker):
    dummy_task_file = '/foo/bar/CERYLE_TASKS'
    find_mock = mocker.patch('ceryle.util.find_task_file', return_value=dummy_task_file)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.context = '/foo/bar'
    task_def.default_task = 'tg1'

    loader = ceryle.TaskFileLoader(dummy_task_file)
    loader.load = mocker.Mock(return_value=task_def)
    loader_cls = mocker.patch('ceryle.TaskFileLoader', return_value=loader)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=False)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 1
    find_mock.assert_called_once_with(mocker.ANY)

    loader_cls.assert_called_once_with(dummy_task_file)
    loader.load.assert_called_once_with()

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1')


def test_main_run_fails_by_task_file_not_found(mocker):
    find_mock = mocker.patch('ceryle.util.find_task_file', return_value=None)

    with pytest.raises(TaskFileError) as e:
        ceryle.main.run()
    assert str(e.value) == 'task file not found'
    find_mock.assert_called_once_with(mocker.ANY)


def test_main_run_raises_by_no_default_and_no_task_to_run(mocker):
    dummy_task_file = '/foo/bar/CERYLE_TASKS'
    find_mock = mocker.patch('ceryle.util.find_task_file', return_value=dummy_task_file)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.context = '/foo/bar'
    task_def.default_task = None

    loader = ceryle.TaskFileLoader(dummy_task_file)
    loader.load = mocker.Mock(return_value=task_def)
    loader_cls = mocker.patch('ceryle.TaskFileLoader', return_value=loader)

    # excercise
    with pytest.raises(TaskDefinitionError) as e:
        ceryle.main.run()
    assert str(e.value) == 'default task is not declared, specify task to run'
