import ceryle
import ceryle.main


def test_main_list_tasks(mocker):
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=[])

    dummy_task_files = [
        '/foo/bar/TASK',
    ]
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=dummy_task_files)

    tg1_t1 = ceryle.Task(ceryle.Command('do some 1'), 'ctx')
    tg1_t2 = ceryle.Task(ceryle.Command('do some 2'), 'ctx')
    tg1 = ceryle.TaskGroup('tg1', [tg1_t1, tg1_t2])

    tg2_t1 = ceryle.Task(ceryle.Command('do some 3'), 'ctx')
    tg2_t2 = ceryle.Task(ceryle.Command('do some 4'), 'ctx')
    tg2 = ceryle.TaskGroup('tg2', [tg2_t1, tg2_t2], dependencies=['tg1'])

    task_def = mocker.Mock()
    task_def.tasks = [tg1, tg2]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    # excercise
    with ceryle.util.std_capture() as (o, e):
        res = ceryle.main.list_tasks(verbose=1)
        lines = o.getvalue().splitlines()

    # verification
    assert res == 0
    assert lines == [
        'tg1:',
        '  tasks:',
        '    %s' % str(tg1.tasks[0].executable),
        '    %s' % str(tg1.tasks[1].executable),
        'tg2:',
        '  dependencies:',
        '    tg1',
        '  tasks:',
        '    %s' % str(tg2.tasks[0].executable),
        '    %s' % str(tg2.tasks[1].executable),
    ]
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_task_files)
