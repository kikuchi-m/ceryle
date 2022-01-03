import os
import re

import pytest

from ceryle.util.capture import std_capture
from ceryle.util import print_stream, indent_s
from ceryle.util.printutils import decorate, ERROR_FONT, StdoutPrinter, StderrPrinter, QuietPrinter, Output


class TestOutputMemory:
    @pytest.mark.parametrize(
        'lines', [
            ['aaa', 'bbb ', 'ccc'],
            [b'aaa', b'bbb ', b'ccc'],
        ])
    def test_writeline(self, lines):
        with Output(100) as output:
            for line in lines:
                output.writeline(line)

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

    @pytest.mark.parametrize(
        'lines', [
            ['aaa', 'bbb ', 'ccc'],
            [b'aaa', b'bbb ', b'ccc'],
        ])
    def test_writeline(self, lines):
        with Output(2) as output:
            for line in lines:
                output.writeline(line)

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


class TestStdoutPrinter:
    def test_printline(self):
        p = StdoutPrinter()
        with std_capture() as (o, _), p.open_output():
            p.printline('default 1 ')
            p.printline('default 2 ')

            assert o.getvalue().rstrip(os.linesep).split(os.linesep) == [
                'default 1 ',
                'default 2 ',
            ]

    def test_stdout_printline_warn(self):
        p = StdoutPrinter(warning_patterns=['^waruning'])
        with std_capture() as (o, _), p.open_output():
            p.printline('warning some... 1 ')
            p.printline('warning some... 2 ')

            assert o.getvalue().rstrip(os.linesep).split(os.linesep) == [
                'warning some... 1 ',
                'warning some... 2 ',
            ]

    def test_output(self):
        p = StdoutPrinter()
        with p.open_output():
            p.printline('out 1')
            p.printline('out 2')

        o = p.get_output()

        assert o.lines() == ['out 1', 'out 2']


class TestSTderrPrinter:
    def test_printline(self):
        p = StderrPrinter()
        with std_capture() as (_, e), p.open_output():
            p.printline('some error 1 ')
            p.printline('some error 2 ')

            lines = e.getvalue().rstrip(os.linesep).split(os.linesep)

            assert re.match('.*some error 1 .*', lines[0])
            assert re.match('.*some error 2 .*', lines[1])

    def test_output(self):
        p = StderrPrinter()
        with std_capture() as (_, e), p.open_output():
            p.printline('out 1')
            p.printline('out 2')

        o = p.get_output()

        assert o.lines() == ['out 1', 'out 2']


class TestQuietPrinter:
    def test_printline(self):
        p = QuietPrinter()
        with std_capture() as (o, _), p.open_output():
            p.printline('default')

            assert '' == o.getvalue().rstrip()

    def test_output(self):
        p = QuietPrinter()
        with std_capture() as (o, _), p.open_output():
            p.printline('out 1')
            p.printline('out 2')

        o = p.get_output()

        assert o.lines() == ['out 1', 'out 2']


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
    for line in lines:
        yield line


def test_print_stream():
    with std_capture() as (o, _):
        out = print_stream(gen_lines())

        assert o.getvalue().splitlines() == ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']
        assert out.lines() == ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']


def test_print_stream_error():
    lines = [decorate(line, ERROR_FONT) for line in ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']]
    with std_capture() as (_, e):
        out = print_stream(gen_lines(), error=True)

        assert e.getvalue().splitlines() == lines
        assert out.lines() == ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']


@pytest.mark.parametrize('error', [False, True])
def test_print_stream_quiet(error):
    with std_capture() as (o, _):
        out = print_stream(gen_lines(), error=error, quiet=True)

        assert o.getvalue().splitlines() == []
        assert out.lines() == ['plain', 'LF', 'CR', 'CRLF', 'plain', 'LF', 'CR', 'CRLF']


def test_indent_s():
    assert indent_s('a', 0) == 'a'
    assert indent_s('a', 4) == '    a'
