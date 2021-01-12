import pathlib
import tempfile

import pytest

from ceryle import Copy, ExecutionResult
from ceryle.dsl.support import Arg, PathArg


def test_copy_file_to_file():
    '''
    src: file1
    dst: dst_dir/dst_file (neither directory nor file exists)
    expected:
      dst_dir/dst_file
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstd = pathlib.Path(tmpd, 'dst_dir')
        dstf = dstd.joinpath('dst_file')

        assert srcf.is_file() is True
        assert dstf.exists() is False

        copy = Copy('file1', str(pathlib.Path('dst_dir', 'dst_file')))
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'


def test_copy_file_to_file_overwrite():
    '''
    src: file1
    dst: dst_dir/dst_file (file exists)
    expected:
      dst_dir/dst_file
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstf = pathlib.Path(tmpd, 'dst_file')
        with open(dstf, 'w') as fp:
            fp.write('existing')

        assert srcf.is_file() is True
        assert dstf.exists() is True

        copy = Copy('file1', 'dst_file')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'


def test_copy_file_into_directory():
    '''
    src: file1
    dst: dst_dir/ (directory exists)
    expected:
      dst_dir/file1
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstd = pathlib.Path(tmpd, 'dst_dir')
        dstd.mkdir(parents=True)
        dstf = dstd.joinpath('file1')

        assert srcf.is_file() is True
        assert dstd.is_dir() is True
        assert dstf.exists() is False

        copy = Copy('file1', 'dst_dir')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'


def test_copy_file_into_directory_overwrite():
    '''
    src: file1
    dst: dst_dir/
      dst_dir/file1
    expected:
      dst_dir/file1
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstd = pathlib.Path(tmpd, 'dst_dir')
        dstd.mkdir(parents=True)
        dstf = dstd.joinpath('file1')
        with open(dstf, 'w') as fp:
            fp.write('existing')

        assert srcf.is_file() is True
        assert dstd.is_dir() is True
        assert dstf.is_file() is True

        copy = Copy('file1', 'dst_dir')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'


def test_copy_directory_to_directory():
    '''
    src: d1/
      d1/f1
    dst: d2 (not exist)
    expected:
      d2/f1
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcd = pathlib.Path(tmpd, 'd1')
        srcd.mkdir(parents=True)
        srcf = srcd.joinpath('f1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstd = pathlib.Path(tmpd, 'd2')
        dstf = dstd.joinpath('f1')

        assert srcf.is_file() is True
        assert dstd.exists() is False

        copy = Copy('d1', 'd2')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'


def test_copy_directory_to_existing_directory():
    '''
    src: d1/
      d1/f1
      d1/d2/f2
    dst: d/d1/ (directory exists)
      d/d1/f3
    expected:
      d/d1/f1
      d/d1/f2
      d/d1/d2/f2
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcd1 = pathlib.Path(tmpd, 'd1')
        srcd2 = srcd1.joinpath('d2')
        srcd2.mkdir(parents=True)
        srcf1 = srcd1.joinpath('f1')
        srcf2 = srcd2.joinpath('f2')
        for p in [srcf1, srcf2]:
            with open(p, 'w') as fp:
                fp.write(f'copy test {p.name}')

        dstd = pathlib.Path(tmpd, 'd', 'd1')
        dstd.mkdir(parents=True)
        dstf1 = dstd.joinpath('f1')
        dstf2 = dstd.joinpath('d2', 'f2')
        xf3 = dstd.joinpath('f3')
        with open(xf3, 'w') as fp:
            fp.write(f'copy test {xf3.name}')

        for p in [srcf1, srcf2, xf3]:
            assert p.is_file() is True
        for p in [dstf1, dstf2]:
            assert p.exists() is False

        copy = Copy('d1', str(pathlib.Path('d', 'd1')))
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        for p in [dstf1, dstf2, xf3]:
            assert p.is_file() is True
            with open(p) as fp:
                assert fp.read().rstrip() == f'copy test {p.name}'


def test_copy_file_not_exists():
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        dstf = pathlib.Path(tmpd, 'dst_file')

        assert srcf.exists() is False

        copy = Copy('file1', 'dst_file')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 1
        assert dstf.exists() is False


def test_copy_glob_files():
    '''
    src: d1/
      d1/f1.txt
      d1/f2.py
      d1/d2/d3/f3.txt
    dst: dst_dir (not exists)
    expected:
      dst_dir/f1.txt
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcd1 = pathlib.Path(tmpd, 'd1')
        srcd2 = srcd1.joinpath('d2')
        srcd2.mkdir(parents=True)
        srcf1 = srcd1.joinpath('f1.txt')
        srcf2 = srcd1.joinpath('f2.py')
        srcf3 = srcd2.joinpath('f3.txt')
        for p in [srcf1, srcf2, srcf3]:
            with open(p, 'w'):
                pass

        dstd = pathlib.Path(tmpd, 'dst_dir')

        for p in [srcf1, srcf2, srcf3]:
            assert p.is_file() is True
        assert dstd.exists() is False

        copy = Copy('d1', 'dst_dir', glob='*.txt')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstd.joinpath('f1.txt').is_file() is True
        assert dstd.joinpath('f2.py').exists() is False
        assert dstd.joinpath('d2', 'd3', 'f3.txt').exists() is False


def test_copy_glob_files_recursive():
    '''
    src: d1/
      d1/f1.txt
      d1/f2.py
      d1/d2/d3/f3.txt
    dst: dst_dir (not exists)
    expected:
      dst_dir/f1.txt
      dst_dir/d2/d3/f3.txt
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcd1 = pathlib.Path(tmpd, 'd1')
        srcd2 = srcd1.joinpath('d2', 'd3')
        srcd2.mkdir(parents=True)
        srcf1 = srcd1.joinpath('f1.txt')
        srcf2 = srcd1.joinpath('f2.py')
        srcf3 = srcd2.joinpath('f3.txt')
        for p in [srcf1, srcf2, srcf3]:
            with open(p, 'w'):
                pass

        dstd = pathlib.Path(tmpd, 'dst_dir')

        for p in [srcf1, srcf2, srcf3]:
            assert p.is_file() is True
        assert dstd.exists() is False

        copy = Copy('d1', 'dst_dir', glob='**/*.txt')
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstd.joinpath('f1.txt').is_file() is True
        assert dstd.joinpath('f2.py').exists() is False
        assert dstd.joinpath('d2', 'd3', 'f3.txt').is_file() is True


@pytest.mark.parametrize(
    'src_arg, dst_arg', [
        (Arg('TEST_SRC', {'TEST_SRC': 'file1'}), Arg('TEST_DST', {'TEST_DST': 'dst_dir/dst_file'})),
        (PathArg('file1'), PathArg('dst_dir', 'dst_file')),
    ])
def test_copy_file_by_arg(src_arg, dst_arg):
    '''
    src: file1
    dst: dst_dir/dst_file (neither directory nor file exists)
    expected:
      dst_dir/dst_file
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        srcf = pathlib.Path(tmpd, 'file1')
        with open(srcf, 'w') as fp:
            fp.write('copy test')

        dstd = pathlib.Path(tmpd, 'dst_dir')
        dstf = dstd.joinpath('dst_file')

        assert srcf.is_file() is True
        assert dstf.exists() is False

        # copy = Copy('file1', str(pathlib.Path('dst_dir', 'dst_file')))
        copy = Copy(src_arg, dst_arg)
        res = copy.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert dstf.is_file() is True
        with open(dstf) as fp:
            assert fp.read().rstrip() == 'copy test'
