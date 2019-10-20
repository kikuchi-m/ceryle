from ceryle import Command, Task, TaskGroup
from ceryle.dsl.parser import parse_tasks


def test_parse():
    raw_tasks = {
        'g1': {
            'tasks': [{
                'run': Command('do some'),
            }, {
                'run': Command('do some more'),
            }],
        },
        'g2': {
            'dependencies': ['g1'],
            'tasks': [{
                'run': Command('do awesome'),
            }],
        },
    }

    tasks = dict([(g.name, g) for g in parse_tasks(raw_tasks, 'context', 'file1.ceryle')])

    assert len(tasks) == 2

    g1 = tasks['g1']
    assert isinstance(g1, TaskGroup)
    assert g1.name == 'g1'
    assert g1.dependencies == []
    assert g1.filename == 'file1.ceryle'

    assert len(g1.tasks) == 2
    assert isinstance(g1.tasks[0], Task)
    assert g1.tasks[0].executable.cmd == ['do', 'some']
    assert g1.tasks[0].context == 'context'
    assert isinstance(g1.tasks[1], Task)
    assert g1.tasks[1].executable.cmd == ['do', 'some', 'more']
    assert g1.tasks[1].context == 'context'

    g2 = tasks['g2']
    assert isinstance(g2, TaskGroup)
    assert g2.name == 'g2'
    assert g2.dependencies == ['g1']
    assert g2.filename == 'file1.ceryle'

    assert len(g2.tasks) == 1
    assert isinstance(g2.tasks[0], Task)
    assert g2.tasks[0].executable.cmd == ['do', 'awesome']
    assert g2.tasks[0].context == 'context'


def test_parse_syntax_suger():
    raw_tasks = {
        'g1': {
            'tasks': [
                Command('do some'),
                Command('do some more'),
            ],
        },
        'g2': [
            Command('do awesome'),
            Command('do awesome more'),
        ],
    }

    tasks = dict([(g.name, g) for g in parse_tasks(raw_tasks, 'context', 'file1.ceryle')])

    assert len(tasks) == 2

    g1 = tasks['g1']
    assert isinstance(g1, TaskGroup)
    assert g1.name == 'g1'
    assert g1.dependencies == []
    assert g1.filename == 'file1.ceryle'

    assert len(g1.tasks) == 2
    assert isinstance(g1.tasks[0], Task)
    assert g1.tasks[0].executable.cmd == ['do', 'some']
    assert isinstance(g1.tasks[1], Task)
    assert g1.tasks[1].executable.cmd == ['do', 'some', 'more']

    g2 = tasks['g2']
    assert isinstance(g2, TaskGroup)
    assert g2.name == 'g2'
    assert g2.dependencies == []
    assert g2.filename == 'file1.ceryle'

    assert len(g2.tasks) == 2
    assert isinstance(g2.tasks[0], Task)
    assert g2.tasks[0].executable.cmd == ['do', 'awesome']
    assert isinstance(g2.tasks[1], Task)
    assert g2.tasks[1].executable.cmd == ['do', 'awesome', 'more']


def test_parse_no_tasks():
    raw_tasks = {
        'g1': {
        },
    }

    tasks = dict([(g.name, g) for g in parse_tasks(raw_tasks, 'context', 'file1.ceryle')])

    assert len(tasks) == 1

    g1 = tasks['g1']
    assert isinstance(g1, TaskGroup)
    assert g1.name == 'g1'
    assert g1.dependencies == []
    assert g1.filename == 'file1.ceryle'

    assert len(g1.tasks) == 0
