import re

from ceryle.util.capture import std_capture
from ceryle.util import print_stream, indent_s
from ceryle.util.printutils import StdoutPrinter, StderrPrinter


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
        lines = [
            'plain',
            'LF\n',
            'CR\r',
            'CRLF\r\n',
            b'plain',
            b'LF\n',
            b'CR\r',
            b'CRLF\r\n',
        ]
        for l in lines:
            yield l

    with std_capture() as (o, _):
        out = print_stream(gen_lines())
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == o.getvalue().splitlines()
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == out


def test_indent_s():
    assert indent_s('a', 0) == 'a'
    assert indent_s('a', 4) == '    a'
