class CeryleException(Exception):
    pass


class IllegalOperation(CeryleException):
    pass


class IllegalFormat(Exception):
    pass


from .const import CERYLE_DIR
from .commands.executable import executable, Executable, ExecutionResult
from .commands.command import Command
from .commands.copy import Copy
from .commands.remove import Remove
from .tasks import TaskDefinitionError, TaskDependencyError, TaskIOError
from .tasks.task import Task, TaskGroup
from .tasks.condition import Condition
from .tasks.resolver import DependencyResolver, DependencyChain
from .tasks.runner import TaskRunner
from .dsl import TaskFileError, NoArgumentError, NoEnvironmentError
from .dsl.loader import TaskFileLoader, TaskDefinition
from .dsl.aggregate_loader import AggregateTaskFileLoader, load_task_files
from .dsl.support import joinpath as path

import datetime as dt
import logging
import pathlib


def configure_logging(level=logging.INFO, console=False, filename=None):
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
                CERYLE_DIR,
                'logs',
                filename or dt.datetime.now().strftime('%Y%m%d-%H%M%S%f.log'))))

    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)8s %(name)s] %(message)s (%(pathname)s:%(lineno)d %(funcName)s)',
        handlers=handlers,
    )
