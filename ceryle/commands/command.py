import logging
import re
import subprocess

from concurrent.futures import ThreadPoolExecutor

from ceryle.commands.executable import Executable
from ceryle.util import print_stream

logger = logging.getLogger(__file__)


class Command(Executable):
    def __init__(self, cmd, cwd=None):
        self._cmd = extract_cmd(cmd)
        self._cwd = cwd

    def execute(self):
        cmd_log = self._cmd_log_message()
        logger.info(f'run command: {cmd_log}')
        proc = subprocess.Popen(
            self._cmd,
            cwd=self._cwd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_std_streams(proc.stdout, proc.stderr)
        logger.info(f'finished {cmd_log}')
        return proc.wait()

    def _cmd_log_message(self):
        if self._cwd:
            return f'[{self.cmd_str()}] ({self._cwd})'
        return f'[{self.cmd_str()}]'

    @property
    def cmd(self):
        return list(self._cmd)

    def cmd_str(self):
        return ' '.join([quote_if_needed(p) for p in self._cmd])


def quote_if_needed(s):
    if ' ' in s:
        return f'"{s}"'
    return s


def extract_cmd(cmd):
    if isinstance(cmd, str):
        trimmed = cmd.strip()
        seed = 0
        parts = []
        while seed >= 0:
            s, seed = next_part(trimmed)
            if s is None:
                break
            parts.append(s)
            trimmed = trimmed[seed:].lstrip()
        return parts
    return cmd


def next_part(cmdstr):
    if len(cmdstr) == 0:
        return None, -1

    m = re.search('[ "]', cmdstr)
    if m:
        span = m.span()
        if m.group() == '"':
            m2 = re.search('"', cmdstr[span[1]:])
            span2 = m2.span()
            return cmdstr[span[1]:span2[0] + 1], span2[1] + 1
        return cmdstr[:span[0]], span[1]
    return cmdstr.strip(), -1


def print_std_streams(stdout, stderr):
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(print_stream, [stdout, stderr], [False, True])
