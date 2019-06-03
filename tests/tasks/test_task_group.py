from ceryle import Command, Task, TaskGroup

def test_new_task_group():
    t1 = Task(Command('do some'))
    t2 = Task(Command('do awwsome'))
    tg = TaskGroup('new_task', [t1, t2])

    assert tg.name == 'new_task'
    assert tg.tasks == [t1, t2]


def test_run_all_tasks(mocker):
    t1 = Task(Command('do some'))
    mocker.patch.object(t1, 'run', return_value=True)

    t2 = Task(Command('do awwsome'))
    mocker.patch.object(t2, 'run', return_value=True)

    tg = TaskGroup('new_task', [t1, t2])
    
    assert tg.run() == True
    t1.run.assert_called_once_with()
    t2.run.assert_called_once_with()


def test_run_fails_some_task(mocker):
    t1 = Task(Command('do some'))
    mocker.patch.object(t1, 'run', return_value=False)

    t2 = Task(Command('do awwsome'))
    mocker.patch.object(t2, 'run', return_value=True)

    tg = TaskGroup('new_task', [t1, t2])
    
    assert tg.run() == False
    t1.run.assert_called_once_with()
    t2.run.assert_not_called()
