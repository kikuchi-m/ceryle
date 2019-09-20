import argparse
import logging
import os
import sys

import ceryle
import ceryle.util as util

logger = logging.getLogger(__name__)


def run(task=None, dry_run=False):
    task_files = util.collect_task_files(os.getcwd())
    logger.info(f'task files: {task_files}')
    if not task_files:
        raise ceryle.TaskFileError('task file not found')
    extensions = util.collect_extension_files(os.getcwd())
    logger.info(f'extensions: {extensions}')

    task_def = ceryle.load_task_files(extensions + task_files)
    if task is None and task_def.default_task is None:
        raise ceryle.TaskDefinitionError('default task is not declared, specify task to run')

    runner = ceryle.TaskRunner(task_def.tasks)
    res = runner.run(task or task_def.default_task, dry_run=dry_run)
    if res is not True:
        return 1
    return 0


def parse_args(argv):
    p = argparse.ArgumentParser()
    # TODO: nargs
    p.add_argument('-n', '--dry-run', action='store_true')
    p.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], default='INFO')
    p.add_argument('--log-stream', action='store_true')

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
        return run(**args)
    except Exception as e:
        logger.error(e)
        if isinstance(e, ceryle.CeryleException):
            util.print_err(str(e))
        else:
            raise e


def entry_point():
    sys.exit(main(sys.argv[1:]))
