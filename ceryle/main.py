import ceryle
import ceryle.util as util
import os


def run(task=None):
    task_file = util.find_task_file(os.getcwd())
    if task_file is None:
        raise ceryle.TaskFileError('task file not found')

    loader = ceryle.TaskFileLoader(task_file)
    task_def = loader.load()

    runner = ceryle.TaskRunner(task_def.tasks)
    res = runner.run(task or task_def.default_task)
    if res is not True:
        return 1
    return 0
