import pathlib
import tempfile

from ceryle.const import DEFAULT_TASK_FILE, CERYLE_DIR, CERYLE_TASK_DIR
from ceryle.util import getin, find_task_file, collect_task_files


def test_getin():
    assert getin({'a': 1}, 'a') == 1
    assert getin({'a': 1}, 'b') is None
    assert getin({'a': 1}, 'a', 'b') is None

    assert getin({0: 1}, 0) == 1

    assert getin({'a': {'b': 2}}, 'a', 'b') == 2
    assert getin({'a': {'b': 2}}, 'a', 'c') is None
    assert getin({'a': {'b': 2}}, 'a', 'b', 'c') is None


def test_getin_returns_default():
    assert getin({'a': 1}, 'b', default=-1) == -1
    assert getin({'a': 1}, 'a', 'b', default=-1) == -1
    assert getin({'a': {'b': 2}}, 'a', 'b', 'c', default=-1) == -1


def prepare_wd(d):
    wd = pathlib.Path(d, 'aa/bb/cc')
    wd.mkdir(parents=True)
    return wd


def test_find_task_file_not_found():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)
        assert pathlib.Path(wd).exists()
        assert find_task_file(wd) is None


def test_find_task_file_found():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)
        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        assert task_file.exists()
        assert find_task_file(wd) == str(task_file)

    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)
        task_file = pathlib.Path(wd.parent.parent, DEFAULT_TASK_FILE)
        task_file.touch()

        assert task_file.exists()
        assert find_task_file(wd) == str(task_file)


def test_collect_task_files_no_task_files(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        assert collect_task_files(wd) == []
        home_mock.assert_called_once_with()


def test_collect_task_files_only_default(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)

        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        expected = [
            str(task_file)
        ]
        assert collect_task_files(wd) == expected
        home_mock.assert_called_once_with()


def test_collect_task_files_additional_task_fils(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)

        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        task_dir = pathlib.Path(wd, CERYLE_DIR, CERYLE_TASK_DIR)
        task_dir.mkdir(parents=True, exist_ok=True)
        additional1 = pathlib.Path(task_dir, 'additional1.ceryle')
        additional1.touch()
        additional2 = pathlib.Path(task_dir, 'additional2.ceryle')
        additional2.touch()

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        expected = [
            str(task_file),
            str(additional1),
            str(additional2),
        ]
        assert collect_task_files(wd) == expected
        home_mock.assert_called_once_with()


def test_collect_task_files_in_home_ceryle_dir(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)

        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        additional1 = pathlib.Path(home_task_dir, 'additional1.ceryle')
        additional1.touch()
        additional2 = pathlib.Path(home_task_dir, 'additional2.ceryle')
        additional2.touch()
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        expected = [
            str(additional1),
            str(additional2),
            str(task_file),
        ]
        assert collect_task_files(wd) == expected
        home_mock.assert_called_once_with()
