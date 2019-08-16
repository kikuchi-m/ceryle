import argparse
import ceryle
import ceryle.util as util
import os


def run(task=None):
    task_files = util.collect_task_files(os.getcwd())
    if not task_files:
        raise ceryle.TaskFileError('task file not found')

    task_def = ceryle.load_task_files(task_files)
    if task is None and task_def.default_task is None:
        raise ceryle.TaskDefinitionError('default task is not declared, specify task to run')

    runner = ceryle.TaskRunner(task_def.tasks)
    res = runner.run(task or task_def.default_task)
    if res is not True:
        return 1
    return 0


def parse_args(argv):
    p = argparse.ArgumentParser()
    # TODO: nargs

    known_args, rest = p.parse_known_args(argv)
    args = vars(known_args)
    args['task'] = rest[0] if len(rest) > 0 else None
    return args


def main(argv):
    return run(**parse_args(argv))
