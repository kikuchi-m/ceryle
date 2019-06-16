import ceryle.main


def test_parse_args():
    argv = ['-t', 'foo']
    args = ceryle.main.parse_args(argv)

    assert args['task'] == 'foo'


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
