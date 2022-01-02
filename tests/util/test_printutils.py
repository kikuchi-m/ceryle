import re

import pytest

from ceryle.util.capture import std_capture
from ceryle.util import print_stream, indent_s
from ceryle.util.printutils import decorate, ERROR_FONT, StdoutPrinter, StderrPrinter, QuietPrinter, Output


class TestOutputMemory:
    def test_writeline(self):
        with Output(100) as output:
            output.writeline('aaa')
            output.writeline('bbb ')
            output.writeline('ccc')

        assert output.lines() == ['aaa', 'bbb ', 'ccc']

    def test_raise_when_already_closed(self):
        with Output(100) as output:
            pass

        with pytest.raises(IOError):
            output.writeline('ccc')

    def test_clean(self):
        with Output(100) as output:
            output.writeline('aaa')

        output.clean()

        with pytest.raises(IOError):
            output.lines()

    def test_from_lines(self):
        output = Output.from_lines(['aaa', 'bbb'])

        assert output.lines() == ['aaa', 'bbb']


class TestOutputFile:
    def test_to_be_file_when_exceeded_threshold(self):
        with Output(2) as output:
            output.writeline('aaa')
            output.writeline('bbb')
            output.writeline('ccc')

        assert isinstance(output._impl, Output._FileOut)

    def test_writeline(self):
        with Output(2) as output:
            output.writeline('aaa')
            output.writeline('bbb ')
            output.writeline('ccc')

        assert output.lines() == ['aaa', 'bbb ', 'ccc']

    def test_raise_when_already_closed(self):
        with Output(2) as output:
            output.writeline('aaa')
            output.writeline('bbb')
            output.writeline('ccc')

        with pytest.raises(IOError):
            output.writeline('ccc')

    def test_clean(self):
        with Output(2) as output:
            output.writeline('aaa')
            output.writeline('bbb')
            output.writeline('ccc')

        output.clean()

        with pytest.raises(IOError):
            output.lines()


def test_stdout_printline():
    p = StdoutPrinter()
    with std_capture() as (o, _):
        p.printline('default')
        assert 'default' == o.getvalue().rstrip()


def test_stdout_printline_warn():
    p = StdoutPrinter(warning_patterns=['^waruning'])
    with std_capture() as (o, _):
        p.printline('warning some...')
        assert 'warning some...' == o.getvalue().rstrip()


def test_stderr_printline():
    p = StderrPrinter()
    with std_capture() as (_, e):
        p.printline('some error')
        assert re.match('.*some error.*', e.getvalue().rstrip())


def test_silent_printline():
    p = QuietPrinter()
    with std_capture() as (o, _):
        p.printline('default')
        assert '' == o.getvalue().rstrip()


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


def test_print_stream():
    with std_capture() as (o, _):
        out = print_stream(gen_lines())
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == o.getvalue().splitlines()
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == out


def test_print_stream_error():
    lines = [decorate(l, ERROR_FONT) for l in ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']]
    with std_capture() as (_, e):
        out = print_stream(gen_lines(), error=True)
        assert lines == e.getvalue().splitlines()
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == out


@pytest.mark.parametrize('error', [False, True])
def test_print_stream_quiet(error):
    with std_capture() as (o, _):
        out = print_stream(gen_lines(), error=error, quiet=True)
        assert [] == o.getvalue().splitlines()
        assert ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF'] == out


def test_indent_s():
    assert indent_s('a', 0) == 'a'
    assert indent_s('a', 4) == '    a'
