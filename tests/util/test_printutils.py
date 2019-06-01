from ceryle.util.printutils import print_stream, StdoutPrinter, StderrPrinter


def test_stdout_printlne():
    p = StdoutPrinter()
    p.printline('default')


def test_stdout_printlne_warn():
    p = StdoutPrinter(warning_patterns=['^waruning'])
    p.printline('warning some...')


def test_stderr_printlne():
    p = StderrPrinter()
    p.printline('some error')


def test_print_stream():
    def gen_lines():
        for l in ['foo', 'bar', 'baz']:
            yield l

    print_stream(gen_lines())
