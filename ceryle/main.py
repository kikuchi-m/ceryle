import argparse
import logging
import os
import sys

import ceryle
import ceryle.util as util

logger = logging.getLogger(__name__)


def load_tasks():
    task_files = util.collect_task_files(os.getcwd())
    logger.info(f'task files: {task_files}')
    if not task_files:
        raise ceryle.TaskFileError('task file not found')
    extensions = util.collect_extension_files(os.getcwd())
    logger.info(f'extensions: {extensions}')

    return ceryle.load_task_files(extensions + task_files)


def run(task=None, dry_run=False, **kwargs):
    task_def = load_tasks()
    if task is None and task_def.default_task is None:
        raise ceryle.TaskDefinitionError('default task is not declared, specify task to run')

    runner = ceryle.TaskRunner(task_def.tasks)
    res = runner.run(task or task_def.default_task, dry_run=dry_run)
    if res is not True:
        return 1
    return 0


def list_tasks(verbose=0):
    task_def = load_tasks()
    groups = sorted(task_def.tasks, key=lambda t: t.name)
    lines = []
    for g in groups:
        lines.append(f'{g.name}:')
        if g.dependencies:
            lines.append(f'  dependencies:')
            for d in g.dependencies:
                lines.append(f'    {d}')
        if verbose > 0 and g.tasks:
            lines.append(f'  tasks:')
            for t in g.tasks:
                lines.append(f'    {t.executable}')
    print(*lines, sep=os.linesep)
    return 0


def parse_args(argv):
    p = argparse.ArgumentParser(allow_abbrev=False)
    p.add_argument('--list-tasks', action='store_true')
    p.add_argument('-n', '--dry-run', action='store_true')
    p.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], default='INFO')
    p.add_argument('--log-stream', action='store_true')
    p.add_argument('-v', '--verbose', action='count', default=0)

    known_args, rest = p.parse_known_args(argv)
    args = vars(known_args)
    args['task'] = rest[0] if len(rest) > 0 else None
    return args


def main(argv):
    args = parse_args(argv)

    ceryle.configure_logging(
        level={
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'ERROR': logging.ERROR,
        }[args.pop('log_level')],
        console=args.pop('log_stream'))
    logger.debug(f'arguments: {argv}')

    try:
        if args.pop('list_tasks', False):
            return list_tasks(verbose=args['verbose'])
        return run(**args)
    except Exception as e:
        logger.error(e)
        if isinstance(e, ceryle.CeryleException):
            util.print_err(str(e))
        else:
            raise e


def entry_point():
    sys.exit(main(sys.argv[1:]))
