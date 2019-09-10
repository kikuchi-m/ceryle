import ceryle.util as util
import logging
import pathlib
import re
import subprocess

from ceryle.commands.executable import Executable, ExecutionResult
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__file__)


class Command(Executable):
    def __init__(self, cmd, cwd=None):
        self._cmd = extract_cmd(cmd)
        self._cwd = cwd

    def execute(self, *args, context=None, **kwargs):
        cmd_log = self._cmd_log_message()
        logger.info(f'run command: {cmd_log}')
        proc = subprocess.Popen(
            self._cmd,
            cwd=self._get_cwd(context),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = print_std_streams(proc.stdout, proc.stderr)
        logger.info(f'finished {cmd_log}')
        return ExecutionResult(proc.wait(), stdout=sout, stderr=serr)

    def _get_cwd(self, context=None):
        if self._cwd:
            cwd = pathlib.Path(self._cwd)
            if cwd.is_absolute():
                return self._cwd
            if context:
                return str(pathlib.Path(context, self._cwd))
            return self._cwd
        return context

    def _cmd_log_message(self):
        if self._cwd:
            return f'[{self.cmd_str()}] ({self._cwd})'
        return f'[{self.cmd_str()}]'

    @property
    def cmd(self):
        return list(self._cmd)

    def cmd_str(self):
        return ' '.join([quote_if_needed(p) for p in self._cmd])

    def __str__(self):
        return self._cmd_log_message()

    def __repr__(self):
        return f'command([{self.cmd_str()}], cwd={self._cwd})'


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
    util.assert_type(cmd, list)
    return list(cmd)


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
        return executor.map(util.print_stream, [stdout, stderr], [False, True])
