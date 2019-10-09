import datetime as dt

from ceryle import IllegalOperation


class StopWatch:
    def __init__(self, start_on_init=False):
        self._beg = None
        self._laps = []
        if start_on_init:
            self._start()

    def start(self):
        self._start()

    def _start(self):
        if not self._beg:
            self._beg = dt.datetime.now()
            self._laps.append(self._beg)

    def elapse(self):
        n = dt.datetime.now()
        total_diff = n - self._beg
        last_diff = n - self._laps[-1]
        self._laps.append(n)
        return total_diff.total_seconds(), last_diff.total_seconds()

    def str_last_lap(self):
        if len(self._laps) == 0:
            raise IllegalOperation('not started')
        if len(self._laps) == 1:
            return '00:00.000 (00:00.000)'
        last = self._laps[-1] - self._laps[-2]
        totla = self._laps[-1] - self._laps[0]
        return f'{_format(last)} ({_format(totla)})'


def _format(delta):
    return f'{delta.seconds // 60:02}:{delta.seconds % 60:02}.{int(delta.microseconds / 1000):03}'
