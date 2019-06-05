import abc
import re
import sys

WARN_FONT = '38;5;221'
ERROR_FONT = '38;5;124'


def sgr(p='0'):
    return f'\x1b[{p}m'


def decorate(s, sgr_pattern):
    return f'{sgr(sgr_pattern)}{s}{sgr()}'


class Printer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def printline(self, line):
        pass


class StdoutPrinter(Printer):
    def __init__(self, warning_patterns=[], warning_font=WARN_FONT,
                 decorate_patterns=[]):
        self._warn = [re.compile(p) for p in warning_patterns]
        self._warn_font = warning_font
        self._decorations = [(re.compile(p), f) for p, f in decorate_patterns]

    def printline(self, line):
        print(self.decorate(line))

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
        self._font = font

    def printline(self, line):
        print_err(line, font=self._font)


def print_stream(s, error=False):
    printer = StderrPrinter() if error else StdoutPrinter()
    for l in s:
        printer.printline((l.decode() if isinstance(l, bytes) else l).rstrip())


def print_err(*lines, font=ERROR_FONT):
    print(*[decorate(l, font) for l in lines], file=sys.stderr)
