class CeryleException(Exception):
    pass


class IllegalOperation(CeryleException):
    pass


from .commands.executable import executable, Executable, ExecutionResult
from .commands.command import Command
from .commands.copy import Copy
from .commands.remove import Remove
from .dsl import TaskFileError
from .dsl.loader import TaskFileLoader, TaskDefinition
from .dsl.aggregate_loader import AggregateTaskFileLoader, load_task_files
from .dsl.support import joinpath as path
from .tasks import TaskDefinitionError, TaskDependencyError, TaskIOError
from .tasks.task import Task, TaskGroup
from .tasks.resolver import DependencyResolver, DependencyChain
from .tasks.runner import TaskRunner
from .const import CERYLE_DIR

import datetime as dt
import logging
import pathlib


def configure_logging(level=logging.INFO, console=False):
    from .util.printutils import print_err

    handlers = []

    logdir = pathlib.Path.home().joinpath(CERYLE_DIR, 'logs')
    if logdir.exists() and not logdir.is_dir():
        print_err(f'{logdir} already exists but not a directory.',
                  'log is not saved.')
    else:
        logdir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.FileHandler(pathlib.Path.home().joinpath(
                CERYLE_DIR, 'logs', dt.datetime.now().strftime('%Y%m%d-%H%M%S%f.log'))))

    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)8s %(name)s] %(message)s (%(pathname)s:%(lineno)d %(funcName)s)',
        handlers=handlers,
    )
