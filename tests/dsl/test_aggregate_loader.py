from ceryle import TaskGroup
from ceryle import AggregateTaskFileLoader, TaskFileLoader, TaskDefinition


def test_load_multiple_task_files(mocker):
    task_def1 = TaskDefinition([TaskGroup('foo', [])], default_task='foo')
    loader1 = TaskFileLoader('file1')
    loader1.load = mocker.Mock(return_value=task_def1)

    task_def2 = TaskDefinition([TaskGroup('bar', [])], default_task='bar')
    loader2 = TaskFileLoader('file2')
    loader2.load = mocker.Mock(return_value=task_def2)

    loader_cls = mocker.patch('ceryle.TaskFileLoader', side_effect=[loader1, loader2])

    loader = AggregateTaskFileLoader(['file1', 'file2'])
    task_def = loader.load()

    assert len(task_def.tasks) == 2
    assert task_def.default_task == 'bar'
    assert loader_cls.call_count == 2
    loader1.load.assert_called_once_with(
        global_vars={},
        local_vars={},
        additional_args={})
    loader2.load.assert_called_once_with(
        global_vars={},
        local_vars={},
        additional_args={})

    assert task_def1.tasks[0] in task_def.tasks
    assert task_def2.tasks[0] in task_def.tasks


def test_load_multiple_task_files_override(mocker):
    task_def1 = TaskDefinition(tasks=[TaskGroup('foo', [])])
    loader1 = TaskFileLoader('file1')
    loader1.load = mocker.Mock(return_value=task_def1)

    task_def2 = TaskDefinition(tasks=[TaskGroup('foo', [])])
    loader2 = TaskFileLoader('file2')
    loader2.load = mocker.Mock(return_value=task_def2)

    loader_cls = mocker.patch('ceryle.TaskFileLoader', side_effect=[loader1, loader2])

    loader = AggregateTaskFileLoader(['file1', 'file2'])
    task_def = loader.load()

    assert len(task_def.tasks) == 1
    assert loader_cls.call_count == 2

    assert task_def2.tasks[0] in task_def.tasks
    assert task_def1.tasks[0] not in task_def.tasks
