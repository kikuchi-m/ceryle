import os
import pathlib

import pytest

import ceryle.commands.builtin as builtin
from ceryle.dsl.support import Arg, Env, PathArg


@pytest.mark.parametrize(
    'target, from_context', [
        ('dir1', pathlib.Path('dir1')),
        ('dir1/dir2', pathlib.Path('dir1/dir2')),
        (pathlib.Path('dir1'), pathlib.Path('dir1')),
        (Arg('TARGET', {'TARGET': 'dir1'}), pathlib.Path('dir1')),
        (Env('TARGET'), pathlib.Path('dir1/dir2')),
        (PathArg('dir1', 'dir2'), pathlib.Path('dir1/dir2')),
        (PathArg('dir1', Arg('SUB_DIR', {'SUB_DIR': 'dir2'})), pathlib.Path('dir1/dir2')),
    ])
def test_create_directory(tmpdir, mocker, target, from_context):
    env = dict(**os.environ.copy(), TARGET='dir1/dir2')
    mocker.patch.dict('os.environ', env)

    expected = pathlib.Path(tmpdir) / from_context
    assert not expected.exists()

    mkdir_exe = builtin.mkdir(target)
    res = mkdir_exe.execute(context=tmpdir)

    assert res.return_code == 0
    assert expected.is_dir()


def test_create_directories(tmpdir):
    context = pathlib.Path(tmpdir)

    expected1 = context / 'dir1'
    expected2 = context / 'dir2' / 'dir3'
    assert not expected1.exists()
    assert not expected2.exists()

    mkdir_exe = builtin.mkdir('dir1', 'dir2/dir3')
    res = mkdir_exe.execute(context=context)

    assert res.return_code == 0
    assert expected1.is_dir()
    assert expected2.is_dir()


def test_create_directory_no_error_when_already_exists(tmpdir):
    context = pathlib.Path(tmpdir)

    expected = context / 'dir1'
    expected.mkdir(parents=True)
    assert expected.exists()

    mkdir_exe = builtin.mkdir('dir1', 'dir2/dir3')
    res = mkdir_exe.execute(context=context)

    assert res.return_code == 0
    assert expected.is_dir()
