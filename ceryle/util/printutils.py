import abc
import logging
import os
import re
import sys

from contextlib import AbstractContextManager
from tempfile import NamedTemporaryFile

import ceryle.util as util

WARN_FONT = '38;5;221'
ERROR_FONT = '38;5;160'

logger = logging.getLogger(__name__)


def sgr(p='0'):
    return f'\x1b[{p}m'


def decorate(s, sgr_pattern):
    return f'{sgr(sgr_pattern)}{s}{sgr()}'


class Printer(metaclass=abc.ABCMeta):
    def __init__(self):
        self._out = None

    @abc.abstractmethod
    def printline(self, line):
        pass

    def open_output(self, max_lines_on_memory=100):
        self._out = Output(max_lines_on_memory)
        return self._out

    def get_output(self):
        return self._out

    def _writeline(self, line):
        self._out.writeline(line)


class StdoutPrinter(Printer):
    def __init__(self,
                 warning_patterns=[],
                 warning_font=WARN_FONT,
                 decorate_patterns=[]):
        super(Printer).__init__()
        self._warn = [re.compile(p) for p in warning_patterns]
        self._warn_font = warning_font
        self._decorations = [(re.compile(p), f) for p, f in decorate_patterns]

    def printline(self, line):
        logger.debug(line)
        print(self.decorate(line))
        self._writeline(line)

    def decorate(self, line):
        for r in self._warn:
            if r.match(line):
                return decorate(line, self._warn_font)
        for r, f in self._decorations:
            if r.match(line):
                return decorate(line, f)
        return line


class StderrPrinter(Printer):
    def __init__(self, font=ERROR_FONT):
        super(Printer).__init__()
        self._font = font

    def printline(self, line):
        print_err(line, font=self._font)
        self._writeline(line)


class QuietPrinter(Printer):
    def __init__(self, font=ERROR_FONT):
        super(Printer).__init__()

    def printline(self, line):
        logger.debug(line)
        self._writeline(line)


class Output(AbstractContextManager):
    ENCODED_SEP = os.linesep.encode()

    def __init__(self, max_lines_on_memory):
        self._max_lines_on_memory = max_lines_on_memory
        self._impl = None

    def writeline(self, line):
        if self._impl.closed:
            raise IOError('output is already closed')
        self._impl.writeline((line if isinstance(line, bytes) else line.encode()).rstrip(Output.ENCODED_SEP))

    def __enter__(self):
        self._impl = Output._MemOut(self, self._max_lines_on_memory)
        return self

    def __exit__(self, *exc):
        self._impl.exit()

    def lines(self):
        if self._impl.cleaned:
            raise IOError('output is already closed')
        return self._impl.lines()

    def clean(self):
        self._impl.clean()

    @staticmethod
    def from_lines(lines):
        ls = [util.assert_type(s, str).encode() for s in util.assert_type(lines, list)]
        with Output(len(ls)) as o:
            o._impl._lines = ls
        return o

    class _OutputImpl(metaclass=abc.ABCMeta):
        @abc.abstractmethod
        def writeline(self, line):
            pass

        @abc.abstractmethod
        def exit(self):
            pass

        @property
        @abc.abstractproperty
        def closed(self):
            pass

        @abc.abstractmethod
        def lines(self):
            pass

        @abc.abstractmethod
        def clean(self):
            pass

        @property
        @abc.abstractproperty
        def cleaned(self):
            pass

    class _MemOut(_OutputImpl):
        def __init__(self, output, max_lines):
            self._max_lines = max_lines
            self._output = output
            self._lines = []
            self._closed = False
            self._cleaned = False

        def writeline(self, line):
            self._lines.append(line)
            if len(self._lines) > self._max_lines:
                o = Output._FileOut()
                for line in self._lines:
                    o.writeline(line)
                self._output._impl = o

        def exit(self):
            self._closed = True

        @property
        def closed(self):
            return self._closed

        def lines(self):
            return [s.decode() for s in self._lines]

        def clean(self):
            self._closed = True
            self._cleaned = True

        @property
        def cleaned(self):
            return self._cleaned

    class _FileOut(_OutputImpl):
        def __init__(self):
            self._tf = NamedTemporaryFile()
            self._flush_per_lines = 100
            self._buf_lines = 0
            self._deleted = False

        def writeline(self, line):
            self._tf.file.write(line + Output.ENCODED_SEP)
            buf = self._buf_lines
            if (buf := buf + 1) >= self._flush_per_lines:
                self._tf.file.flush()
                buf = 0
            self._buf_lines = buf

        def exit(self):
            self._tf.file.close()

        @property
        def closed(self):
            return self._tf.closed

        def lines(self):
            with open(self._tf.name) as fp:
                return [s.rstrip(os.linesep) for s in fp]

        def clean(self):
            self._tf.close()
            self._deleted = True

        @property
        def cleaned(self):
            return self._deleted


def print_stream(s, error=False, quiet=False):
    printer = {
        1: StdoutPrinter,
        2: StderrPrinter,
        4: QuietPrinter,
    }[quiet << 2 or error << 1 or 1]()
    out = []
    with printer.open_output():
        for line in s:
            decoded = str.rstrip(line.decode() if isinstance(line, bytes) else line)
            printer.printline(decoded)
            out.append(decoded)
    return out


def print_out(*lines, level=logging.DEBUG):
    logger.log(level, os.linesep.join(lines))
    print(*lines, sep=os.linesep)


def print_err(*lines, font=ERROR_FONT):
    logger.debug(os.linesep.join(lines))
    print(*[decorate(lines, font) for lines in lines], sep=os.linesep, file=sys.stderr)


def indent_s(s, depth):
    return ' ' * depth + s
