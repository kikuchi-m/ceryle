import pathlib

import ceryle
import ceryle.main


def test_main_show_tree(mocker):
    script_dir = pathlib.Path(__file__).parent

    tg1_t1 = ceryle.Task(ceryle.Command('do some 1 1'), 'ctx')
    tg1_t2 = ceryle.Task(ceryle.Command('do some 1 2'), 'ctx')
    tg1 = ceryle.TaskGroup('tg1', [tg1_t1, tg1_t2], str(script_dir.joinpath('file1.ceryle')))

    tg2_t1 = ceryle.Task(ceryle.Command('do some 2 1'), 'ctx')
    tg2_t2 = ceryle.Task(ceryle.Command('do some 2 2'), 'ctx')
    tg2 = ceryle.TaskGroup('tg2', [tg2_t1, tg2_t2], str(script_dir.joinpath('file1.ceryle')),
                           dependencies=['tg1'])

    tg3_t1 = ceryle.Task(ceryle.Command('do some 3'), 'ctx')
    tg3 = ceryle.TaskGroup('tg3', [tg3_t1], str(script_dir.joinpath('file2.ceryle')))

    tg4_t1 = ceryle.Task(ceryle.Command('do some 4'), 'ctx')
    tg4 = ceryle.TaskGroup('tg4', [tg4_t1], str(script_dir.joinpath('file2.ceryle')),
                           dependencies=['tg2', 'tg3'])

    task_def = ceryle.TaskDefinition([tg1, tg2, tg3, tg4], default_task='tg4')
    load_mock = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, '/foo/bar'))

    mocker.patch('pathlib.Path.cwd', return_value=script_dir.parent.joinpath('foo'))

    # excercise
    with ceryle.util.std_capture() as (o, e):
        res = ceryle.main.show_tree(verbose=1)
        lines = o.getvalue().splitlines()

    # verification
    assert res == 0
    assert lines == [
        'tg4: (../tests/file2.ceryle)',
        '  dependencies:',
        '    tg2: (../tests/file1.ceryle)',
        '      dependencies:',
        '        tg1: (../tests/file1.ceryle)',
        '          tasks:',
        '            %s' % str(tg1.tasks[0].executable),
        '            %s' % str(tg1.tasks[1].executable),
        '      tasks:',
        '        %s' % str(tg2.tasks[0].executable),
        '        %s' % str(tg2.tasks[1].executable),
        '    tg3: (../tests/file2.ceryle)',
        '      tasks:',
        '        %s' % str(tg3.tasks[0].executable),
        '  tasks:',
        '    %s' % str(tg4.tasks[0].executable),
    ]
    load_mock.assert_called_once()


def test_main_show_tree_skip_already_depending(mocker):
    script_dir = pathlib.Path(__file__).parent

    tg1_t1 = ceryle.Task(ceryle.Command('do some 1 1'), 'ctx')
    tg1_t2 = ceryle.Task(ceryle.Command('do some 1 2'), 'ctx')
    tg1 = ceryle.TaskGroup('tg1', [tg1_t1, tg1_t2], str(script_dir.joinpath('file1.ceryle')))

    tg2_t1 = ceryle.Task(ceryle.Command('do some 2 1'), 'ctx')
    tg2_t2 = ceryle.Task(ceryle.Command('do some 2 2'), 'ctx')
    tg2 = ceryle.TaskGroup('tg2', [tg2_t1, tg2_t2], str(script_dir.joinpath('file1.ceryle')),
                           dependencies=['tg1'])

    tg3_t1 = ceryle.Task(ceryle.Command('do some 3'), 'ctx')
    tg3 = ceryle.TaskGroup('tg3', [tg3_t1], str(script_dir.joinpath('file2.ceryle')),
                           dependencies=['tg1'])

    tg4_t1 = ceryle.Task(ceryle.Command('do some 4'), 'ctx')
    tg4 = ceryle.TaskGroup('tg4', [tg4_t1], str(script_dir.joinpath('file2.ceryle')),
                           dependencies=['tg2', 'tg3'])

    task_def = ceryle.TaskDefinition([tg1, tg2, tg3, tg4], default_task='tg4')
    load_mock = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, '/foo/bar'))

    # excercise
    with ceryle.util.std_capture() as (o, e):
        res = ceryle.main.show_tree()
        lines = o.getvalue().splitlines()

    # verification
    assert res == 0
    assert lines == [
        'tg4:',
        '  dependencies:',
        '    tg2:',
        '      dependencies:',
        '        tg1:',
        '    tg3:',
    ]
    load_mock.assert_called_once()
