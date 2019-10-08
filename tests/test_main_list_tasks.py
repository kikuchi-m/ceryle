import pytest

import ceryle
import ceryle.main

TASKS = [
    ceryle.TaskGroup(
        'tg1', [
            ceryle.Task(ceryle.Command('do some 1'), '/foo/bar'),
            ceryle.Task(ceryle.Command('do some 2'), '/foo/bar'),
        ],
        dependencies=[]),
    ceryle.TaskGroup(
        'tg2', [
            ceryle.Task(ceryle.Command('do some 3'), '/foo/bar'),
            ceryle.Task(ceryle.Command('do some 4'), '/foo/bar'),
        ],
        dependencies=['tg1']),
]

LIST_TASKS_PARAMS = [
    (0, [
        'tg1',
        'tg2',
    ]),
    (1, [
        'tg1:',
        'tg2:',
        '  dependencies:',
        '    tg1',
    ]),
    (2, [
        'tg1:',
        '  tasks:',
        '    %s' % str(TASKS[0].tasks[0].executable),
        '    %s' % str(TASKS[0].tasks[1].executable),
        'tg2:',
        '  dependencies:',
        '    tg1',
        '  tasks:',
        '    %s' % str(TASKS[1].tasks[0].executable),
        '    %s' % str(TASKS[1].tasks[1].executable),
    ]),
]


@pytest.fixture
def mockup_load_tasks(mocker, tmpdir):
    task_def = mocker.Mock()
    task_def.tasks = TASKS
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, '/foo/bar'))
    return load_mock, task_def


@pytest.mark.parametrize(
    'verbose, expected_lines',
    LIST_TASKS_PARAMS,
    ids=['v0', 'v1', 'v2'])
def test_main_list_tasks(mocker, mockup_load_tasks, verbose, expected_lines):
    load_mock, task_def = mockup_load_tasks

    # excercise
    with ceryle.util.std_capture() as (o, e):
        res = ceryle.main.list_tasks(verbose=verbose)
        lines = o.getvalue().splitlines()

    # verification
    assert res == 0
    assert lines == expected_lines
    load_mock.assert_called_once()
