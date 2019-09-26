import ceryle.main


def test_parse_args():
    argv = ['foo']
    args = ceryle.main.parse_args(argv)

    assert args['task'] == 'foo'
    assert args['dry_run'] is False
    assert args['list_tasks'] is False


def test_main_run(mocker):
    run_mock = mocker.patch('ceryle.main.run', return_value=0)

    rc = ceryle.main.main([])

    assert rc == 0
    run_mock.assert_called_once()


def test_main_list_tasks(mocker):
    run_mock = mocker.patch('ceryle.main.run', return_value=0)
    list_tasks_mock = mocker.patch('ceryle.main.list_tasks', return_value=0)

    rc = ceryle.main.main(['--list-tasks'])

    assert rc == 0
    run_mock.assert_not_called()
    list_tasks_mock.assert_called_once_with(verbose=mocker.ANY)
