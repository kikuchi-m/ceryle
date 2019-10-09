import re
import time

from ceryle.util import StopWatch


def test_stopwatch():
    sw = StopWatch()
    sw.start()
    str0 = sw.str_last_lap()

    time.sleep(0.5)
    total1, lap1 = sw.elapse()
    str1 = sw.str_last_lap()

    time.sleep(0.3)
    total2, lap2 = sw.elapse()
    str2 = sw.str_last_lap()

    assert 0.5 <= total1 and total1 < 0.8
    assert 0.5 <= lap1 and lap1 < 0.6

    assert 0.8 <= total2 and total2 < 1.0
    assert 0.3 <= lap2 and lap2 < 0.4

    print(str0, str1, str2)
    assert re.match(r'^00:00.000 \(00:00\.000\)$', str0) is not None
    assert re.match(r'^00:00\.5[\d]{2} \(00:00\.5[\d]{2}\)$', str1) is not None
    assert re.match(r'^00:00\.3[\d]{2} \(00:00\.8[\d]{2}\)$', str2) is not None
