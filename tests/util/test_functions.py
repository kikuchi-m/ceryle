import pathlib
import tempfile

from ceryle.const import DEFAULT_TASK_FILE
from ceryle.util import getin, find_task_file


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


def test_find_task_file(mocker):
    def prepare_wd(d):
        wd = pathlib.Path(d, 'aa/bb/cc')
        wd.mkdir(parents=True)
        return wd

    with tempfile.TemporaryDirectory() as tmpd:
        wd = prepare_wd(tmpd)
        assert pathlib.Path(wd).exists()
        assert find_task_file(wd) is None

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
