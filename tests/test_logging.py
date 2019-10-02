import datetime as dt
import pathlib
import tempfile

import pytest

import ceryle
from ceryle.const import CERYLE_DIR

FIXED_DT = dt.datetime(2019, 1, 2, 3, 4, 5)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class DatetimeMock:
        @staticmethod
        def now():
            return FIXED_DT

    monkeypatch.setattr(dt, 'datetime', DatetimeMock)


def test_generate_log_dir_and_save_logs(mocker, patch_datetime_now):
    with tempfile.TemporaryDirectory() as tmpd:
        mocker.patch('pathlib.Path.home', return_value=pathlib.Path(tmpd))

        logdir = pathlib.Path(tmpd, CERYLE_DIR, 'logs')
        assert logdir.exists() is False

        ceryle.configure_logging()
        assert logdir.exists() is True

        logfile = pathlib.Path(tmpd, CERYLE_DIR, 'logs', FIXED_DT.strftime('%Y%m%d-%H%M%S%f.log'))
        assert logfile.exists() is True

        # ### could not disable pytest to capture logs
        # logger = logging.getLogger('logging-test')
        # logger.debug('logging test: debug')
        # logger.info('logging test: info')
        # with open(logfile) as fp:
        #     logs = [l.rstrip() for l in fp.readlines()]
        # assert len(logs) == 1
        # assert re.match('.*\\[ *INFO.*\\] logging test: info.*', logs[0])
