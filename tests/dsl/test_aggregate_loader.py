from ceryle import TaskGroup
from ceryle import AggregateTaskFileLoader, TaskFileLoader, ExtensionLoader, TaskDefinition


def test_load_multiple_task_files(mocker):
    mock = mocker.Mock()

    task_def1 = TaskDefinition([TaskGroup('foo', [], 'context', 'file1')], default_task='foo')
    loader1 = TaskFileLoader('file1.ceryle')
    loader1.load = mocker.Mock(return_value=task_def1)
    mock.attach_mock(loader1.load, 'loader1_load')

    task_def2 = TaskDefinition([TaskGroup('bar', [], 'context', 'file2')], default_task='bar')
    loader2 = TaskFileLoader('file2')
    loader2.load = mocker.Mock(return_value=task_def2)
    mock.attach_mock(loader2.load, 'loader2_load')

    loader_cls = mocker.patch('ceryle.TaskFileLoader', side_effect=[loader1, loader2])
    mock.attach_mock(loader_cls, 'loader_cls')

    loader = AggregateTaskFileLoader(['file1', 'file2'])
    task_def = loader.load()

    assert len(task_def.tasks) == 2
    assert task_def.default_task == 'bar'
    assert mock.mock_calls == [
        mocker.call.loader_cls('file1'),
        mocker.call.loader1_load(local_vars={}, additional_args={}),
        mocker.call.loader_cls('file2'),
        mocker.call.loader2_load(local_vars={}, additional_args={}),
    ]

    assert task_def1.tasks[0] in task_def.tasks
    assert task_def2.tasks[0] in task_def.tasks


def test_load_multiple_task_files_override(mocker):
    task_def1 = TaskDefinition(tasks=[TaskGroup('foo', [], 'context', 'file1')])
    loader1 = TaskFileLoader('file1')
    loader1.load = mocker.Mock(return_value=task_def1)

    task_def2 = TaskDefinition(tasks=[TaskGroup('foo', [], 'context', 'file2')])
    loader2 = TaskFileLoader('file2')
    loader2.load = mocker.Mock(return_value=task_def2)

    loader_cls = mocker.patch('ceryle.TaskFileLoader', side_effect=[loader1, loader2])

    loader = AggregateTaskFileLoader(['file1', 'file2'])
    task_def = loader.load()

    assert len(task_def.tasks) == 1
    assert loader_cls.call_count == 2

    assert task_def2.tasks[0] in task_def.tasks
    assert task_def1.tasks[0] not in task_def.tasks


def test_load_multiple_task_files_with_extensions(mocker):
    mock = mocker.Mock()

    task_def1 = TaskDefinition([TaskGroup('foo', [], 'context', 'file1')], default_task='foo')
    loader1 = TaskFileLoader('file1')
    loader1.load = mocker.Mock(return_value=task_def1)
    mock.attach_mock(loader1.load, 'loader1_load')

    task_def2 = TaskDefinition([TaskGroup('bar', [], 'context', 'file2')], default_task='bar')
    loader2 = TaskFileLoader('file2')
    loader2.load = mocker.Mock(return_value=task_def2)
    mock.attach_mock(loader2.load, 'loader2_load')

    loader_cls = mocker.patch('ceryle.TaskFileLoader', side_effect=[loader1, loader2])
    mock.attach_mock(loader_cls, 'loader_cls')

    extensions = {'my_cmd': 'dummy'}
    xloader = ExtensionLoader('xfile1')
    xloader.load = mocker.Mock(return_value=extensions)
    mock.attach_mock(xloader.load, 'xloader_load')

    xloader_cls = mocker.patch('ceryle.ExtensionLoader', side_effect=[xloader])
    mock.attach_mock(xloader_cls, 'xloader_cls')

    loader = AggregateTaskFileLoader(['file1', 'file2'], extensions=['xfile1'])
    task_def = loader.load()

    assert len(task_def.tasks) == 2
    assert task_def.default_task == 'bar'
    assert mock.mock_calls == [
        mocker.call.xloader_cls('xfile1'),
        mocker.call.xloader_load(local_vars={}, additional_args={}),
        mocker.call.loader_cls('file1'),
        mocker.call.loader1_load(local_vars=extensions, additional_args={}),
        mocker.call.loader_cls('file2'),
        mocker.call.loader2_load(local_vars=extensions, additional_args={}),
    ]

    assert task_def1.tasks[0] in task_def.tasks
    assert task_def2.tasks[0] in task_def.tasks
