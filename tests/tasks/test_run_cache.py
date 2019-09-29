import pathlib
import tempfile

from ceryle import RunCache


def test_add_result():
    cache = RunCache('tg1')
    cache.add_result(('tg2', True))
    cache.add_result(('tg3', False))
    cache.update_register({
        'tg2': {
            'OUT21': ['aaa', 'bbb'],
            'OUT22': ['ccc', 'ddd'],
        },
    })

    assert cache.task_name == 'tg1'
    assert cache.results == [
        ('tg2', True),
        ('tg3', False),
    ]
    assert cache.register == {
        'tg2': {
            'OUT21': ['aaa', 'bbb'],
            'OUT22': ['ccc', 'ddd'],
        },
    }


def test_save_and_load():
    cache = RunCache('tg1')
    cache.add_result(('tg2', True))
    cache.add_result(('tg3', False))
    cache.update_register({
        'tg2': {
            'OUT21': ['aaa', 'bbb'],
            'OUT22': ['ccc', 'ddd'],
        },
    })

    with tempfile.TemporaryDirectory() as tmpd:
        wd = pathlib.Path(tmpd, '.ceryle')
        wd.mkdir(parents=True)
        cache_file = wd.joinpath('last-execution')

        cache.save(str(cache_file))
        assert cache_file.is_file() is True

        loaded = RunCache.load(cache_file)

    assert isinstance(loaded, RunCache)
    assert loaded.task_name == 'tg1'
    assert loaded.results == [
        ('tg2', True),
        ('tg3', False),
    ]
    assert loaded.register == {
        'tg2': {
            'OUT21': ['aaa', 'bbb'],
            'OUT22': ['ccc', 'ddd'],
        },
    }
