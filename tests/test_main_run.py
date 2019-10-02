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
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    util_expected_calls = [
        mocker.call.collect_tasks_mock(mocker.ANY),
        mocker.call.collect_ex_mock(mocker.ANY),
    ]
    assert util_mocks.mock_calls == util_expected_calls

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False)
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
        ceryle.TaskGroup('tg1', []),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=True)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run(task='tg2')

    # verification
    assert res == 0
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg2', dry_run=False)


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
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.default_task = 'tg1'
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    runner = mocker.Mock()
    runner.run = mocker.Mock(return_value=False)
    runner_cls = mocker.patch('ceryle.TaskRunner', return_value=runner)

    # excercise
    res = ceryle.main.run()

    # verification
    assert res == 1
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})

    runner_cls.assert_called_once_with(task_def.tasks)
    runner.run.assert_called_once_with('tg1', dry_run=False)


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
        ceryle.TaskGroup('tg1', []),
    ]
    task_def.default_task = None
    load_mock = mocker.patch('ceryle.load_task_files', return_value=task_def)

    # excercise
    with pytest.raises(TaskDefinitionError) as e:
        ceryle.main.run()
    assert str(e.value) == 'default task is not declared, specify task to run'
    collect_tasks_mock.assert_called_once_with(mocker.ANY)
    collect_ex_mock.assert_called_once_with(mocker.ANY)
    load_mock.assert_called_once_with(dummy_extensions + dummy_task_files, additional_args={})


def test_main_run_save_last_execution_to_file(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_FILENAME)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], dependencies=['g2']),
        ceryle.TaskGroup('tg2', []),
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
    runner.run.assert_called_once_with('tg1', dry_run=False)


def test_main_run_keep_last_execution_when_dry_run(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.joinpath(const.CERYLE_DIR).mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_FILENAME)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], dependencies=['g2']),
        ceryle.TaskGroup('tg2', []),
    ]
    task_def.default_task = 'tg1'
    load_tasks = mocker.patch('ceryle.main.load_tasks', return_value=(task_def, str(context)))
    save_run_cache = mocker.patch('ceryle.main.save_run_cache')

    existing_run_cache = ceryle.RunCache('tg1')
    existing_run_cache.add_result(('g2', True))
    existing_run_cache.add_result(('g1', False))
    existing_run_cache.update_register({'g2': {'G2T1_STDOUT': ['aaa', 'bbb']}})
    existing_run_cache.save(run_cache_file)

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
    runner.run.assert_called_once_with('tg1', dry_run=True)


def test_main_run_save_last_execution_to_file_even_when_exeption_raised(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_FILENAME)

    task_def = mocker.Mock()
    task_def.tasks = [
        ceryle.TaskGroup('tg1', [], dependencies=['g2']),
        ceryle.TaskGroup('tg2', []),
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
    runner.run.assert_called_once_with('tg1', dry_run=False)


def test_main_save_run_cache(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_FILENAME)

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


def test_main_save_run_cache_handle_exception(mocker, tmpdir):
    context = pathlib.Path(tmpdir, 'foo', 'bar')
    context.mkdir(parents=True)
    run_cache_file = pathlib.Path(context, const.CERYLE_DIR, const.CERYLE_RUN_CACHE_FILENAME)

    run_cache = ceryle.RunCache('tg1')
    mocker.patch.object(run_cache, 'save', side_effect=Exception('test'))

    # excercise
    ceryle.main.save_run_cache(str(context), run_cache)

    # verification
    assert run_cache_file.exists() is False
