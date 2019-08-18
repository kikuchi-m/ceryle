import ceryle.main


def test_parse_args():
    argv = ['foo']
    args = ceryle.main.parse_args(argv)

    assert args['task'] == 'foo'
    assert args['dry_run'] is False


def test_parse_args_dry_run():
    for argv in [['-n'], ['--dry-run']]:
        args = ceryle.main.parse_args(argv)

        assert args['dry_run'] is True


def test_main(mocker):
    args = {
        'task': None,
    }
    parse_mock = mocker.patch('ceryle.main.parse_args', return_value=args)
    run_mock = mocker.patch('ceryle.main.run', return_value=0)

    rc = ceryle.main.main([])

    assert rc == 0
    parse_mock.assert_called_once_with(mocker.ANY)
    run_mock.assert_called_once_with(task=None)
