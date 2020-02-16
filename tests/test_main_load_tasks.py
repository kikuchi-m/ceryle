import pytest

import ceryle.main

from ceryle import TaskFileError


def test_main_load_tasks(mocker):
    context = 'test/context'
    task_files = ['task1.ceryle']
    collect_task_files = mocker.patch('ceryle.util.collect_task_files', return_value=(task_files, context))

    extension_files = ['ex1.py']
    collect_extension_files = mocker.patch('ceryle.util.collect_extension_files', return_value=extension_files)

    task_def = {
        'tasks':  [
            'dummy task group1',
            'dummy task group2',
        ],
        'default_task': 'tg1',
    }
    load_task_files = mocker.patch('ceryle.load_task_files', return_value=task_def)

    d, c = ceryle.main.load_tasks()

    assert d == task_def
    assert c == context
    collect_task_files.assert_called_once()
    collect_extension_files.assert_called_once()
    load_task_files.assert_called_once_with(task_files, extension_files, context, additional_args={})


def test_main_load_tasks_with_args(mocker):
    context = 'test/context'
    task_files = ['task1.ceryle']
    collect_task_files = mocker.patch('ceryle.util.collect_task_files', return_value=(task_files, context))

    extension_files = ['ex1.py']
    collect_extension_files = mocker.patch('ceryle.util.collect_extension_files', return_value=extension_files)

    load_task_files = mocker.patch('ceryle.load_task_files')

    args = {'ARG1': 'foo'}
    ceryle.main.load_tasks(additional_args=args)

    collect_task_files.assert_called_once()
    collect_extension_files.assert_called_once()
    load_task_files.assert_called_once_with(task_files, extension_files, context, additional_args=args)


def test_main_load_tasks_raises_by_no_task_files(mocker):
    context = 'test/context'
    task_files = []
    collect_task_files = mocker.patch('ceryle.util.collect_task_files', return_value=(task_files, context))

    collect_extension_files = mocker.patch('ceryle.util.collect_extension_files')

    load_task_files = mocker.patch('ceryle.load_task_files')

    with pytest.raises(TaskFileError) as e:
        ceryle.main.load_tasks()

    assert str(e.value) == 'task file not found'
    collect_task_files.assert_called_once()
    collect_extension_files.assert_not_called()
    load_task_files.assert_not_called()
