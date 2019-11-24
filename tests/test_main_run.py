import pathlib
import pytest

import ceryle
import ceryle.const as const
import ceryle.main

from ceryle import TaskDefinitionError, TaskFileError


def test_main_run_default_task_group(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    home = pathlib.Path(tmpdir, 'home')
    home.mkdir(parents=True)

    util_mocks = mocker.Mock()
    dummy_extensions = [
        str(home.joinpath('.ceryle', 'extensions', 'x1.py')),
        str(context.joinpath('.ceryle', 'extensions', 'x2.py')),
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)
    util_mocks.attach_mock(collect_ex_mock, 'collect_ex_mock')

    dummy_task_files = [
        str(home.joinpath('.ceryle', 'tasks', 'a.ceryle')),
        str(context.joinpath('CERYLE')),
        str(context.joinpath('.ceryle', 'tasks', 'b.ceryle')),
    ]
    collect_tasks_mock = mocker.patch(
        'ceryle.util.collect_task_files',
        return_value=(dummy_task_files, str(context)))
    util_mocks.attach_mock(collect_tasks_mock, 'collect_tasks_mock')

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle'),
        ceryle.TaskGroup('tg2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_task_files = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_task_files.assert_called_once_with(dummy_task_files, dummy_extensions, additional_args={})

    util_expected_calls = [
        mocker.call.collect_tasks_mock(mocker.ANY),
        mocker.call.collect_ex_mock(mocker.ANY),
    ]
    assert util_mocks.mock_calls == util_expected_calls

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False, last_run=None)
    # resolver_cls.assert_called_once_with({'tg1': ['tg2'], 'tg2': [], 'tg3': []})
    # resolver.validate.assert_called_once_with()
    # resolver.deps_chain_map.assert_called_once_with()


def test_main_run_specific_task_group(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    home = pathlib.Path(tmpdir, 'home')
    home.mkdir(parents=True)

    dummy_extensions = [
        str(home.joinpath('.ceryle', 'extensions', 'x1.py')),
        str(context.joinpath('.ceryle', 'extensions', 'x2.py')),
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        str(home.joinpath('.ceryle', 'tasks', 'a.ceryle')),
        str(context.joinpath('CERYLE')),
        str(context.joinpath('.ceryle', 'tasks', 'b.ceryle')),
    ]
    collect_tasks_mock = mocker.patch(
        'ceryle.util.collect_task_files',
        return_value=(dummy_task_files, str(context)))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle'),
        ceryle.TaskGroup('tg2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_task_files = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(task='tg2')

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_task_files.assert_called_once_with(dummy_task_files, dummy_extensions, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg2', dry_run=False, last_run=None)


def test_main_run_fails_by_task_failure(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    home = pathlib.Path(tmpdir, 'home')
    home.mkdir(parents=True)

    dummy_extensions = [
        str(home.joinpath('.ceryle', 'extensions', 'x1.py')),
        str(context.joinpath('.ceryle', 'extensions', 'x2.py')),
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        str(home.joinpath('.ceryle', 'tasks', 'a.ceryle')),
        str(context.joinpath('CERYLE')),
        str(context.joinpath('.ceryle', 'tasks', 'b.ceryle')),
    ]
    collect_tasks_mock = mocker.patch(
        'ceryle.util.collect_task_files',
        return_value=(dummy_task_files, str(context)))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_task_files = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=False)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 1
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_task_files.assert_called_once_with(dummy_task_files, dummy_extensions, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False, last_run=None)


def test_main_run_fails_by_task_file_not_found(mocker):
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=[])
    collect_tasks_mock = mocker.patch('ceryle.util.collect_task_files', return_value=([], None))

    with pytest.raises(TaskFileError) as e:
        ceryle.main.run()
    assert str(e.value) == 'task file not found'
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_not_called()


def test_main_run_raises_by_no_default_and_no_task_to_run(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    home = pathlib.Path(tmpdir, 'home')
    home.mkdir(parents=True)

    dummy_extensions = [
        str(home.joinpath('.ceryle', 'extensions', 'x1.py')),
        str(context.joinpath('.ceryle', 'extensions', 'x2.py')),
    ]
    collect_ex_mock = mocker.patch('ceryle.util.collect_extension_files', return_value=dummy_extensions)

    dummy_task_files = [
        str(context.joinpath('CERYLE')),
    ]
    collect_tasks_mock = mocker.patch(
        'ceryle.util.collect_task_files',
        return_value=(dummy_task_files, str(context)))

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle'),
    ]
    task_def.default_task = None
    load_task_files = mocker.patch('ceryle.load_task_files', return_value=task_def)

    # excercise
    with pytest.raises(TaskDefinitionError) as e:
        ceryle.main.run()
    assert str(e.value) == 'default task is not declared, specify task to run'
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_task_files.assert_called_once_with(dummy_task_files, dummy_extensions, additional_args={})


def test_main_run_save_last_execution_to_file(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle', dependencies=['g2']),
        ceryle.TaskGroup('tg2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')

    run_cache = ceryle.RunCache('tg1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', True))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})
    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner.get_cache = mocker.Mock(return_value=run_cache)
    mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 0
    save_run_cache.assert_called_once_with(mocker.ANY, mocker.ANY)
    save_run_cache_args, _ = save_run_cache.call_args
    assert save_run_cache_args[0] == str(context)
    assert save_run_cache_args[1].task_name == 'tg1'
    assert save_run_cache_args[1].results == [
        ('g2', True),
        ('g1', True),
    ]
    assert save_run_cache_args[1].register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }

    load_tasks.assert_called_once()
    runner.run.assert_called_once_with('tg1', dry_run=False, last_run=None)


def test_main_run_keep_last_execution_when_dry_run(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.joinpath(const.CERYLE_DIR).mkdir(parents=True)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle', dependencies=['g2']),
        ceryle.TaskGroup('tg2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')

    run_cache = ceryle.RunCache('tg1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', True))
    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner.get_cache = mocker.Mock(return_value=run_cache)
    mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(dry_run=True)

    # verification
    assert res == 0
    save_run_cache.assert_not_called()

    load_tasks.assert_called_once()
    runner.run.assert_called_once_with('tg1', dry_run=True, last_run=None)


def test_main_run_continue_last_run(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.joinpath(const.CERYLE_DIR).mkdir(parents=True)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2']),
        ceryle.TaskGroup('g2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'g1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')

    existing_run_cache = ceryle.RunCache('g1')
    existing_run_cache.add_result(('g2', True))
    existing_run_cache.add_result(('g1', False))
    load_run_cache = mocker.patch('ceryle.main.load_run_cache', return_value=existing_run_cache)

    run_cache = ceryle.RunCache('g1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', True))
    runner = ceryle.TaskRunner(task_def.tasks)
    mocker.patch.object(runner, 'run', return_value=True)
    mocker.patch.object(runner, 'get_cache', return_value=run_cache)
    mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(continue_last_run=True)

    # verification
    assert res == 0
    load_run_cache.assert_called_once_with(str(context), 'g1')
    save_run_cache.assert_called_once()
    runner.run.assert_called_once_with('g1', dry_run=False, last_run=mocker.ANY)
    _, runner_run_kwargs = runner.run.call_args
    last_run = runner_run_kwargs['last_run']
    assert last_run.task_name == 'g1'
    assert last_run.results == [
        ('g2', True),
        ('g1', False),
    ]

    load_tasks.assert_called_once()


def test_main_run_continue_last_run_but_cache_not_found(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.joinpath(const.CERYLE_DIR).mkdir(parents=True)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('g1', [], 'file1.ceryle', dependencies=['g2']),
        ceryle.TaskGroup('g2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'g1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')
    load_run_cache = mocker.patch('ceryle.main.load_run_cache', return_value=None)

    run_cache = ceryle.RunCache('g1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', True))
    runner = ceryle.TaskRunner(task_def.tasks)
    mocker.patch.object(runner, 'run', return_value=True)
    mocker.patch.object(runner, 'get_cache', return_value=run_cache)
    mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(continue_last_run=True)

    # verification
    assert res == 0
    load_run_cache.assert_called_once_with(str(context), 'g1')
    save_run_cache.assert_called_once()
    runner.run.assert_called_once_with('g1', dry_run=False, last_run=None)
    load_tasks.assert_called_once()


def test_main_run_save_last_execution_to_file_even_when_exeption_raised(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], 'file1.ceryle', dependencies=['g2']),
        ceryle.TaskGroup('tg2', [], 'file1.ceryle'),
    ]
    task_def.default_task = 'tg1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')

    run_cache = ceryle.RunCache('tg1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', False))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})
    runner = mocker.Mock()
    runner.run = mocker.Mock(side_effect=Exception('test'))
    runner.get_cache = mocker.Mock(return_value=run_cache)
    mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    with pytest.raises(Exception):
        ceryle.main.run()

    # verification
    save_run_cache.assert_called_once_with(mocker.ANY, mocker.ANY)
    save_run_cache_args, _ = save_run_cache.call_args
    assert save_run_cache_args[0] == str(context)
    assert save_run_cache_args[1].task_name == 'tg1'
    assert save_run_cache_args[1].results == [
        ('g2', True),
        ('g1', False),
    ]
    assert save_run_cache_args[1].register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }

    load_tasks.assert_called_once()
    runner.run.assert_called_once_with('tg1', dry_run=False, last_run=None)


def test_main_save_run_cache(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'tg1')

    run_cache = ceryle.RunCache('tg1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', False))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})

    # excercise
    ceryle.main.save_run_cache(str(context), run_cache)

    # verification
    assert run_cache_file.is_file() is True
    loaded_run_cache = ceryle.RunCache.load(str(run_cache_file))
    assert loaded_run_cache.task_name == 'tg1'
    assert loaded_run_cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert loaded_run_cache.register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }


def test_main_save_run_cache_into_home_ceryle_dir(mocker, tmpdir):
    home = pathlib.Path(tmpdir, 'home')
    home.joinpath(const.CERYLE_DIR).mkdir(parents=True)
    run_cache_file = pathlib.Path(home, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'tg1')
    home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(home))

    run_cache = ceryle.RunCache('tg1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', False))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})

    # excercise
    ceryle.main.save_run_cache(None, run_cache)

    # verification
    assert run_cache_file.is_file() is True
    loaded_run_cache = ceryle.RunCache.load(str(run_cache_file))
    assert loaded_run_cache.task_name == 'tg1'
    assert loaded_run_cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert loaded_run_cache.register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }
    home_mock.assert_called_once()


def test_main_save_run_cache_handle_exception(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'tg1')

    run_cache = ceryle.RunCache('tg1')
    mocker.patch.object(run_cache, 'save', side_effect=Exception('test'))

    # excercise
    ceryle.main.save_run_cache(str(context), run_cache)

    # verification
    assert run_cache_file.exists() is False


def test_main_load_run_cache(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'xxx')
    run_cache_file.parent.mkdir(parents=True)

    run_cache = ceryle.RunCache('g1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', False))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})
    run_cache.save(str(run_cache_file))

    # excercise
    loaded_run_cache = ceryle.main.load_run_cache(str(context), 'xxx')

    # verification
    assert loaded_run_cache.task_name == 'g1'
    assert loaded_run_cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert loaded_run_cache.register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }


def test_main_load_run_cache_from_home_ceryle_dir(mocker, tmpdir):
    home = pathlib.Path(tmpdir, 'home')
    run_cache_file = pathlib.Path(home, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'xxx')
    run_cache_file.parent.mkdir(parents=True)
    home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(home))

    run_cache = ceryle.RunCache('g1')
    run_cache.add_result(('g2', True))
    run_cache.add_result(('g1', False))
    run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})
    run_cache.save(str(run_cache_file))

    # excercise
    loaded_run_cache = ceryle.main.load_run_cache(None, 'xxx')

    # verification
    assert loaded_run_cache.task_name == 'g1'
    assert loaded_run_cache.results == [
        ('g2', True),
        ('g1', False),
    ]
    assert loaded_run_cache.register == {
        'g2': {
            'G2T1_STDOUT': ['aaa', 'bbb'],
        },
    }
    home_mock.assert_called_once()


def test_main_load_run_cache_return_none_if_cache_file_not_found(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'xxx')
    run_cache_file.parent.mkdir(parents=True)

    # excercise
    assert ceryle.main.load_run_cache(str(context), 'xxx') is None


def test_main_load_run_cache_from_home_ceryle_dir_return_none_if_cache_file_not_found(mocker, tmpdir):
    home = pathlib.Path(tmpdir, 'home')
    run_cache_file = pathlib.Path(home, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_DIRNAME, 'xxx')
    run_cache_file.parent.mkdir(parents=True)
    home_mock = mocker.patch('pathlib.Path.home', return_value=pathlib.Path(home))

    # excercise
    assert ceryle.main.load_run_cache(None, 'xxx') is None
    home_mock.assert_called_once()
