import os
import pathlib
import tempfile

from ceryle import Remove, ExecutionResult


def test_remove_files():
    '''
    context:
      f1
      d/f2
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        f1 = pathlib.Path(tmpd, 'f1')
        f2 = pathlib.Path(tmpd, 'd', 'f2')
        f2.parent.mkdir(parents=True)
        for f in [f1, f2]:
            with open(f, 'w'):
                pass
            assert f.is_file() is True

        remove = Remove(
            'f1',
            str(pathlib.Path('d', 'f2')))
        res = remove.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        for f in [f1, f2]:
            assert f.exists() is False
        assert f2.parent.is_dir() is True


def test_remove_directory_tree():
    '''
    context:
      d1/f1
      d1/d2/f2
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        f1 = pathlib.Path(tmpd, 'd1', 'f1')
        f2 = pathlib.Path(tmpd, 'd1', 'd2', 'f2')
        f2.parent.mkdir(parents=True)
        for f in [f1, f2]:
            with open(f, 'w'):
                pass
            assert f.is_file() is True

        remove = Remove('d1')
        res = remove.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert pathlib.Path(tmpd, 'd1').exists() is False


def test_remove_directory_tree_containing_symlinks():
    '''
    context:
      d1/f1
      d1/l1 -> f1
      d1/l3 -> d2
      d1/d2/l2 -> ../f1
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        f1 = pathlib.Path(tmpd, 'd1', 'f1')
        f1.parent.mkdir(parents=True)
        with open(f1, 'w'):
            pass
        assert f1.is_file() is True

        l1 = pathlib.Path(tmpd, 'd1', 'l1')
        l2 = pathlib.Path(tmpd, 'd1', 'd2', 'l2')
        l3 = pathlib.Path(tmpd, 'd1', 'd2', 'l3')
        l2.parent.mkdir(parents=True)
        for l in [l1, l2]:
            l.symlink_to(os.path.relpath(f1, l.parent))
            assert l.is_symlink() is True
            assert l.is_file() is True
        l3.symlink_to(os.path.relpath(l2.parent, l3.parent))
        assert l3.is_symlink() is True
        assert l3.is_dir() is True

        remove = Remove('d1')
        res = remove.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert pathlib.Path(tmpd, 'd1').exists() is False


def test_remove_directory_tree_containing_symlinks_to_outside_of_direcotry():
    '''
    context:
      d1/d2/l1 -> ../../d3/f1
      d1/d2/l2 -> ../../d3/d4
      d3/f1
      d3/d4/f2
    '''
    with tempfile.TemporaryDirectory() as tmpd:
        f1 = pathlib.Path(tmpd, 'd3', 'f1')
        f2 = pathlib.Path(tmpd, 'd3', 'd4', 'f2')
        f2.parent.mkdir(parents=True)
        for f in [f1, f2]:
            with open(f, 'w'):
                pass
            assert f.is_file() is True

        l1 = pathlib.Path(tmpd, 'd1', 'l1')
        l2 = pathlib.Path(tmpd, 'd1', 'l2')
        l2.parent.mkdir(parents=True)
        l1.symlink_to(os.path.relpath(f1, l1.parent))
        assert l1.is_symlink() is True
        assert l1.is_file() is True
        l2.symlink_to(os.path.relpath(f2.parent, l2.parent))
        assert l2.is_symlink() is True
        assert l2.is_dir() is True

        remove = Remove('d1')
        res = remove.execute(context=tmpd)

        assert isinstance(res, ExecutionResult)
        assert res.return_code == 0
        assert pathlib.Path(tmpd, 'd1').exists() is False
        for f in [f1, f2]:
            assert f.is_file() is True