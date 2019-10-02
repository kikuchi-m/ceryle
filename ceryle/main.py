import argparse
import logging
import os
import pathlib
import re
import sys

import ceryle
import ceryle.const as const
import ceryle.util as util

logger = logging.getLogger(__name__)


def load_tasks(additional_args={}):
    task_files, root_context = util.collect_task_files(os.getcwd())
    logger.info(f'task files: {task_files}')
    if not task_files:
        raise ceryle.TaskFileError('task file not found')
    extensions = util.collect_extension_files(os.getcwd())
    logger.info(f'extensions: {extensions}')

    return ceryle.load_task_files(extensions + task_files, additional_args=additional_args), root_context


def run(task=None, dry_run=False, additional_args={},
        continue_last_run=False):

    task_def, root_context = load_tasks(additional_args=additional_args)
    if task is None and task_def.default_task is None:
        raise ceryle.TaskDefinitionError('default task is not declared, specify task to run')

    runner = ceryle.TaskRunner(task_def.tasks)
    last_run = load_run_cache(root_context) if continue_last_run else None
    try:
        res = runner.run(task or task_def.default_task, dry_run=dry_run, last_run=last_run)
    finally:
        not dry_run and save_run_cache(root_context, runner.get_cache())
    if res is not True:
        return 1
    return 0


def save_run_cache(root_context, run_cache):
    try:
        cache_file = _run_cache_file(root_context)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        run_cache.save(str(cache_file))
    except Exception as e:
        logger.error(e)
        util.print_err('failed to save last execution result', str(e))


def load_run_cache(root_context):
    cache_file = _run_cache_file(root_context)
    if cache_file.is_file():
        return ceryle.RunCache.load(str(cache_file))
    return None


def _run_cache_file(root_context):
    return pathlib.Path(root_context or pathlib.Path.home(),
                        const.CERYLE_DIR,
                        const.CERYLE_RUN_CACHE_FILENAME)


def list_tasks(verbose=0):
    task_def, _ = load_tasks()
    groups = sorted(task_def.tasks, key=lambda t: t.name)
    lines = []
    for g in groups:
        lines.append(f'{g.name}:')
        if g.dependencies:
            lines.append(util.indent_s('dependencies:', 2))
            for d in g.dependencies:
                lines.append(util.indent_s(str(d), 4))
        if verbose > 0 and g.tasks:
            lines.append(util.indent_s('tasks:', 2))
            for t in g.tasks:
                lines.append(util.indent_s(str(t.executable), 4))
    print(*lines, sep=os.linesep)
    return 0


def show_tree(task=None, verbose=0):
    task_def, _ = load_tasks()
    if task is None and task_def.default_task is None:
        raise ceryle.TaskDefinitionError('default task is not declared, specify task to show info')

    tg = task_def.find_task_group(task or task_def.default_task)
    if tg is None:
        raise ceryle.TaskDefinitionError(f'{task or task_def.default_task} not found')

    lines = []

    def _append(g, depth):
        lines.append(util.indent_s(f'{g.name}:', depth * 4))
        if g.dependencies:
            lines.append(util.indent_s('dependencies:', depth * 4 + 2))
        for d in g.dependencies:
            _append(task_def.find_task_group(d), depth + 1)
        if verbose > 0 and g.tasks:
            lines.append(util.indent_s('tasks:', depth * 4 + 2))
            for t in g.tasks:
                lines.append(util.indent_s(f'{t.executable}', depth * 4 + 4))
    _append(tg, 0)
    print(*lines, sep=os.linesep)
    return 0


def parse_args(argv):
    p = argparse.ArgumentParser(allow_abbrev=False)
    p.add_argument('--list-tasks', action='store_true')
    p.add_argument('--show', action='store_true')
    p.add_argument('-n', '--dry-run', action='store_true')
    p.add_argument('--continue', action='store_true')
    p.add_argument('--arg', action='append', default=[])
    p.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], default='INFO')
    p.add_argument('--log-stream', action='store_true')
    p.add_argument('--log-filename')
    p.add_argument('-v', '--verbose', action='count', default=0)

    known_args, rest = p.parse_known_args(argv)
    args = vars(known_args)
    args.update(continue_last_run=args.pop('continue'))
    args['additional_args'] = read_args(args.pop('arg'))
    args['task'] = rest[0] if len(rest) > 0 else None
    return args


def read_args(args):
    res = {}
    reg = re.compile('^([^=]+)=(.*)')
    for a in args:
        m = reg.match(a)
        if not m:
            raise ceryle.IllegalFormat(f'{a} is illegal foramt for --arg option, must be NAME=VALUE')
        res.update({m.group(1): remove_quotes_if_needed(m.group(2))})
    return res


def remove_quotes_if_needed(v):
    if (v.startswith('"') and v.endswith('"')) or (v.startswith('\'') and v.endswith('\'')):
        return v[1:-1]
    if v.startswith('\\"') and v.endswith('\\"'):
        return v[1:-2] + '"'
    return v


def main(argv):
    args = parse_args(argv)

    ceryle.configure_logging(
        level={
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'ERROR': logging.ERROR,
        }[args.pop('log_level')],
        console=args.pop('log_stream'),
        filename=args.pop('log_filename'))
    logger.debug(f'arguments: {argv}')

    try:
        if args.pop('list_tasks', False):
            return list_tasks(verbose=args['verbose'])
        if args.pop('show', False):
            return show_tree(task=args['task'], verbose=args['verbose'])
        return run(**args)
    except Exception as e:
        logger.error(e)
        if isinstance(e, ceryle.CeryleException):
            util.print_err(str(e))
        else:
            raise e


def entry_point():
    sys.exit(main(sys.argv[1:]))
