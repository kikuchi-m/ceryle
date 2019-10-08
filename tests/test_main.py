import pytest

import ceryle.main
from ceryle import IllegalFormat


def test_parse_args():
    argv = ['foo']
    args = ceryle.main.parse_args(argv)

    assert args['task'] == 'foo'
    assert args['dry_run'] is False
    assert args['continue_last_run'] is False
    assert args['list_tasks'] is False
    assert args['show'] is False
    assert args['verbose'] == 0
    assert args['additional_args'] == {}


@pytest.mark.parametrize(
    'argv,verbose',
    [(['-v'], 1), (['-vv'], 2)])
def test_parse_args_verbose(argv, verbose):
    args = ceryle.main.parse_args(argv)

    assert args['task'] is None
    assert args['verbose'] == verbose


def test_parse_args_runtime_argumens():
    argv = [
        '--arg', 'ARG1=aaa',
        '--arg', 'ARG2="b c"',
        '--arg', 'ARG3=\'b c\'',
        '--arg', 'ARG4=\\"xyz\\"',
        '--arg', 'ARG5=a"b',
        'foo',
    ]
    args = ceryle.main.parse_args(argv)

    assert args['task'] == 'foo'
    assert args['dry_run'] is False
    assert args['list_tasks'] is False
    assert args['show'] is False
    assert args['additional_args'] == {
        'ARG1': 'aaa',
        'ARG2': 'b c',
        'ARG3': 'b c',
        'ARG4': '"xyz"',
        'ARG5': 'a"b',
    }


def test_parse_args_illegal_format_arg_option():
    with pytest.raises(IllegalFormat):
        ceryle.main.parse_args(['--arg', 'a'])


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


def test_main_show_tree(mocker):
    run_mock = mocker.patch('ceryle.main.run', return_value=0)
    show_tree_mock = mocker.patch('ceryle.main.show_tree', return_value=0)

    rc = ceryle.main.main(['--show'])

    assert rc == 0
    run_mock.assert_not_called()
    show_tree_mock.assert_called_once_with(task=None, verbose=mocker.ANY)
