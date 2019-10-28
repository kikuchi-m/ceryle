import pathlib

from ceryle import save_input_to, ExecutionResult


def test_save_input_to(tmpdir):
    context = pathlib.Path(tmpdir, 'context')
    outpath = pathlib.Path('output', 'stdout.log')

    cmd_save = save_input_to(str(outpath))
    res = cmd_save.execute(context=str(context), inputs=['aaa', 'bbb', 'ccc'])

    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0

    with open(context.joinpath(outpath)) as fp:
        lines = [l.rstrip() for l in fp.readlines()]

    assert lines == ['aaa', 'bbb', 'ccc']


def test_save_input_to_fails_since_file_exists(tmpdir):
    context = pathlib.Path(tmpdir, 'context')
    outpath = pathlib.Path('output', 'stdout.log')
    abs_outpath = context.joinpath(outpath)
    abs_outpath.parent.mkdir(parents=True)
    with open(abs_outpath, 'w') as fp:
        fp.write('xxx')

    cmd_save = save_input_to(str(outpath))
    res = cmd_save.execute(context=str(context), inputs=['aaa', 'bbb', 'ccc'])

    assert isinstance(res, ExecutionResult)
    assert res.return_code == 1

    with open(abs_outpath) as fp:
        lines = [l.rstrip() for l in fp.readlines()]

    assert lines == ['xxx']


def test_save_input_to_overwrite(tmpdir):
    context = pathlib.Path(tmpdir, 'context')
    outpath = pathlib.Path('output', 'stdout.log')
    abs_outpath = context.joinpath(outpath)
    abs_outpath.parent.mkdir(parents=True)
    with open(abs_outpath, 'w') as fp:
        fp.write('xxx')

    cmd_save = save_input_to(str(outpath), overwrite=True)
    res = cmd_save.execute(context=str(context), inputs=['aaa', 'bbb', 'ccc'])

    assert isinstance(res, ExecutionResult)
    assert res.return_code == 0

    with open(abs_outpath) as fp:
        lines = [l.rstrip() for l in fp.readlines()]

    assert lines == ['aaa', 'bbb', 'ccc']
