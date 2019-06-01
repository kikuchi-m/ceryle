import contextlib
import io
import sys


@contextlib.contextmanager
def std_capture():
    stdout = sys.stdout
    stderr = sys.stderr
    with io.StringIO() as out, io.StringIO() as err:
        try:
            sys.stdout = out
            sys.stderr = err
            yield out, err
        finally:
            sys.stdout = stdout
            sys.stderr = stderr
