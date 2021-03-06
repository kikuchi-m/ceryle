import pathlib
import tempfile

from ceryle.const import DEFAULT_TASK_FILE, CERYLE_DIR, CERYLE_TASK_DIR, CERYLE_EX_DIR, CERYLE_EX_FILE_EXT
from ceryle.util import getin, find_task_file, collect_task_files, collect_extension_files


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


def test_find_task_file_not_found():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)
        assert pathlib.Path(wd).exists()
        assert find_task_file(wd) is None


def test_find_task_file_not_found_if_directory():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)
        wd.joinpath(DEFAULT_TASK_FILE).mkdir()
        assert pathlib.Path(wd).exists()
        assert wd.joinpath(DEFAULT_TASK_FILE).is_dir()
        assert find_task_file(wd) is None


def test_find_task_file_found():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        assert task_file.exists()
        assert find_task_file(wd) == str(task_file)

    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        task_file = pathlib.Path(wd.parent.parent, DEFAULT_TASK_FILE)
        task_file.touch()

        assert task_file.exists()
        assert find_task_file(wd) == str(task_file)


def test_collect_task_files_no_task_files(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        assert collect_task_files(wd) == ([], None)
        home_mock.assert_called_once_with()


def test_collect_task_files_only_default(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
        task_file.touch()

        home_task_dir = pathlib.Path(tmpd, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
        home_task_dir.mkdir(parents=True, exist_ok=True)
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        expected = [
            str(task_file)
        ]
        assert collect_task_files(wd) == (expected, str(wd))
        home_mock.assert_called_once_with()


def test_collect_task_files_additional_task_fils(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

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
        assert collect_task_files(wd) == (expected, str(wd))
        home_mock.assert_called_once_with()


def test_collect_task_files_additional_task_fils_in_subdirs(mocker, tmpdir):
    wd = pathlib.Path(tmpdir, 'aa/bb/cc')
    wd.mkdir(parents=True)

    task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
    task_file.touch()

    task_dir_base = pathlib.Path(wd, CERYLE_DIR, CERYLE_TASK_DIR)
    task_dir_sub1 = task_dir_base.joinpath('x')
    task_dir_sub1.mkdir(parents=True, exist_ok=True)
    task_dir_sub2 = task_dir_base.joinpath('y/z')
    task_dir_sub2.mkdir(parents=True, exist_ok=True)

    additional1 = pathlib.Path(task_dir_sub1, 'additional1.ceryle')
    additional1.touch()
    additional2 = pathlib.Path(task_dir_sub2, 'additional2.ceryle')
    additional2.touch()

    home_dir = pathlib.Path(tmpdir, 'home')
    home_dir.mkdir(parents=True, exist_ok=True)
    home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpdir, 'home'))

    expected = [
        str(task_file),
        str(additional1),
        str(additional2),
    ]
    assert collect_task_files(wd) == (expected, str(wd))
    home_mock.assert_called_once_with()


def test_collect_task_files_in_home_ceryle_dir(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

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
        assert collect_task_files(wd) == (expected, str(wd))
        home_mock.assert_called_once_with()


def test_collect_task_files_in_subdirs_in_home_ceryle_dir(mocker, tmpdir):
    wd = pathlib.Path(tmpdir, 'aa/bb/cc')
    wd.mkdir(parents=True)

    task_file = pathlib.Path(wd, DEFAULT_TASK_FILE)
    task_file.touch()

    home_task_dir = pathlib.Path(tmpdir, 'home', CERYLE_DIR, CERYLE_TASK_DIR)
    home_task_dir_sub1 = home_task_dir.joinpath('x')
    home_task_dir_sub1.mkdir(parents=True, exist_ok=True)
    home_task_dir_sub2 = home_task_dir.joinpath('y/z')
    home_task_dir_sub2.mkdir(parents=True, exist_ok=True)

    additional1 = pathlib.Path(home_task_dir_sub1, 'additional1.ceryle')
    additional1.touch()
    additional2 = pathlib.Path(home_task_dir_sub2, 'additional2.ceryle')
    additional2.touch()
    home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpdir, 'home'))

    expected = [
        str(additional1),
        str(additional2),
        str(task_file),
    ]
    assert collect_task_files(wd) == (expected, str(wd))
    home_mock.assert_called_once_with()


def test_collect_extension_files_no_extensions():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        ceryle_dir = pathlib.Path(wd, CERYLE_DIR, CERYLE_EX_DIR)
        ceryle_dir.mkdir(parents=True)

        assert collect_extension_files(wd) == []


def test_collect_extension_files_in_ceryle_dir():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)

        ex_dir = wd.joinpath(CERYLE_DIR, CERYLE_EX_DIR)
        ex_dir.mkdir(parents=True)
        task_file = wd.joinpath(DEFAULT_TASK_FILE)
        task_file.touch()
        for ex in ['a', 'b']:
            p = ex_dir.joinpath(ex + CERYLE_EX_FILE_EXT)
            p.touch()
            assert p.is_file() is True

        expected = [
            str(ex_dir.joinpath('a' + CERYLE_EX_FILE_EXT)),
            str(ex_dir.joinpath('b' + CERYLE_EX_FILE_EXT)),
        ]
        assert collect_extension_files(str(wd)) == expected


def test_collect_extension_files_in_ceryle_dir_at_upper_hierarchy():
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)
        ex_dir = wd.parent.parent.joinpath(CERYLE_DIR, CERYLE_EX_DIR)
        ex_dir.mkdir(parents=True)
        task_file = wd.parent.parent.joinpath(DEFAULT_TASK_FILE)
        task_file.touch()
        for ex in ['a', 'b']:
            p = ex_dir.joinpath(ex + CERYLE_EX_FILE_EXT)
            p.touch()
            assert p.is_file() is True

        expected = [
            str(ex_dir.joinpath('a' + CERYLE_EX_FILE_EXT)),
            str(ex_dir.joinpath('b' + CERYLE_EX_FILE_EXT)),
        ]
        assert collect_extension_files(str(wd)) == expected


def test_collect_extension_files_in_home(mocker):
    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, 'aa/bb/cc')
        wd.mkdir(parents=True)
        ex_dir = wd.joinpath(CERYLE_DIR, CERYLE_EX_DIR)
        ex_dir.mkdir(parents=True)
        task_file = wd.joinpath(DEFAULT_TASK_FILE)
        task_file.touch()
        for ex in ['a', 'b']:
            p = ex_dir.joinpath(ex + CERYLE_EX_FILE_EXT)
            p.touch()
            assert p.is_file() is True

        home_ex_dir = pathlib.Path(tmpd, 'home').joinpath(CERYLE_DIR, CERYLE_EX_DIR)
        home_ex_dir.mkdir(parents=True)
        for ex in ['a', 'b']:
            p = home_ex_dir.joinpath(ex + CERYLE_EX_FILE_EXT)
            p.touch()
            assert p.is_file() is True
        home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd, 'home'))

        expected = [
            str(home_ex_dir.joinpath('a' + CERYLE_EX_FILE_EXT)),
            str(home_ex_dir.joinpath('b' + CERYLE_EX_FILE_EXT)),
            str(ex_dir.joinpath('a' + CERYLE_EX_FILE_EXT)),
            str(ex_dir.joinpath('b' + CERYLE_EX_FILE_EXT)),
        ]
        assert collect_extension_files(str(wd)) == expected
        home_mock.assert_called_once_with()
