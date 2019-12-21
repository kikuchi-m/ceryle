import logging
import os
import pathlib
import re
import subprocess

from concurrent.futures import ThreadPoolExecutor

import ceryle.util as util
from ceryle import CeryleException
from ceryle.commands.executable import Executable, ExecutionResult

logger = logging.getLogger(__name__)


class Command(Executable):
    def __init__(self, cmd, cwd=None, inputs_as_args=False, env={}):
        self._cmd = extract_cmd(cmd)
        self._cwd = util.assert_type(cwd, None, str, pathlib.Path)
        self._as_args = util.assert_type(inputs_as_args, bool)
        self._env = util.assert_type(env, dict)

    def execute(self, context=None, inputs=[], timeout=None):
        cmd_log = self._cmd_log_message()
        logger.info(f'run command: {cmd_log}')

        communicate = False
        cmd, env = self.preprocess(self.cmd, self._env)
        if len(inputs) > 0:
            if self._as_args:
                cmd = cmd + inputs
            else:
                communicate = True
        logger.debug(f'actual command: {cmd}')
        logger.debug(f'additional environment variables: {env}')
        proc = subprocess.Popen(
            ['cmd', '/C', *cmd] if util.is_win() else cmd,
            cwd=self._get_cwd(context),
            env=self._with_os_env(env),
            stdin=subprocess.PIPE if communicate else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if communicate:
            stds = proc.communicate(input=os.linesep.join(inputs).encode(), timeout=timeout)
            o, e = print_std_streams(*[std.decode().rstrip().split(os.linesep) for std in stds])
        else:
            o, e = print_std_streams(proc.stdout, proc.stderr)
            proc.wait()

        res = ExecutionResult(proc.returncode, stdout=o, stderr=e)
        logger.info(f'finished with {proc.returncode} {cmd_log}')
        logger.debug(res)
        return res

    def _get_cwd(self, context=None):
        if self._cwd:
            cwd = pathlib.Path(self._cwd)
            if cwd.is_absolute():
                return self._cwd
            if context:
                return str(pathlib.Path(context, self._cwd))
            return self._cwd
        return context

    def _with_os_env(self, env):
        e = os.environ.copy()
        e.update(env)
        return e

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
    if isinstance(s, str) and ' ' in s:
        return f'"{s}"'
    return str(s)


def extract_cmd(cmd):
    if isinstance(cmd, str):
        trimmed = cmd.strip()
        seed = 0
        parts = []
        while seed >= 0:
            s, seed = next_part(trimmed)
            if s is None:
                if seed is None:
                    raise CommandFormatError(f'invalid command format: [{cmd}]')
                break
            parts.append(s)
            trimmed = trimmed[seed:].lstrip()
    else:
        parts = util.assert_type(cmd, list)
    if util.is_win() and isinstance(parts[0], str) and parts[0].startswith('./'):
        return [str(pathlib.Path(parts[0])), *parts[1:]]
    return parts


def next_part(cmdstr):
    if len(cmdstr) == 0:
        return None, -1

    m = re.search(r'[ "]', cmdstr)
    if m:
        span = m.span()
        if m.group() == '"':
            if cmdstr[span[0] - 1] == '\\':
                s, seed = next_part(cmdstr[span[1]:])
                if s is None:
                    return f'{cmdstr[:span[0]]}"', seed
                return f'{cmdstr[:span[0]]}"{s}', (span[1] + seed) if seed > -1 else seed
            m2 = re.search('"', cmdstr[span[1]:])
            if m2 is None:
                return None, None
            span2 = m2.span()
            return cmdstr[span[1]:span2[0] + 1], span2[1] + 1
        return cmdstr[:span[0]], span[1]
    return cmdstr.strip(), -1


def print_std_streams(stdout, stderr):
    with ThreadPoolExecutor(max_workers=2) as executor:
        return executor.map(util.print_stream, [stdout, stderr], [False, True])


class CommandFormatError(CeryleException):
    pass
