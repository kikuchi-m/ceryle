import re

from ceryle.util.capture import std_capture
from ceryle.util.printutils import print_stream, StdoutPrinter, StderrPrinter


def test_stdout_printlne():
    p = StdoutPrinter()
    with std_capture() as (o, _):
        p.printline('default')
        assert 'default' == o.getvalue().rstrip()


def test_stdout_printlne_warn():
    p = StdoutPrinter(warning_patterns=['^waruning'])
    with std_capture() as (o, _):
        p.printline('warning some...')
        assert 'warning some...' == o.getvalue().rstrip()


def test_stderr_printlne():
    p = StderrPrinter()
    with std_capture() as (_, e):
        p.printline('some error')
        assert re.match('.*some error.*', e.getvalue().rstrip())


def test_print_stream():
    def gen_lines():
        for l in ['foo', 'bar', 'baz']:
            yield l

    with std_capture() as (o, _):
        out = print_stream(gen_lines())
        assert ['foo', 'bar', 'baz'] == o.getvalue().splitlines()
        assert ['foo', 'bar', 'baz'] == out
