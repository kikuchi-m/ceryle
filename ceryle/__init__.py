__version__ = '0.2.2'

class CeryleException(Exception):
    pass


class IllegalOperation(RuntimeError):
    pass


class IllegalFormat(Exception):
    pass


from .commands.executable import executable, executable_with, Executable, ExecutionResult
from .commands.command import Command, CommandFormatError
from .commands.copy import Copy
from .commands.remove import Remove
from .commands.builtin import save_input_to
from .tasks import TaskDefinitionError, TaskDependencyError, TaskIOError
from .tasks.task import Task, TaskGroup
from .tasks.condition import Condition
from .tasks.resolver import DependencyResolver, DependencyChain
from .tasks.runner import TaskRunner, RunCache
from .dsl import TaskFileError, NoArgumentError, NoEnvironmentError
from .dsl.loader import TaskFileLoader, ExtensionLoader, TaskDefinition
from .dsl.aggregate_loader import AggregateTaskFileLoader, load_task_files
from .dsl.support import joinpath as path

import datetime as dt
import logging
import pathlib


def configure_logging(level=logging.INFO, console=False, filename=None):
    import ceryle.const as const
    import ceryle.util as util

    handlers = []

    logdir = pathlib.Path.home().joinpath(const.CERYLE_DIR, 'logs')
    if logdir.exists() and not logdir.is_dir():
        util.print_err(f'{logdir} already exists but not a directory.',
                       'log is not saved.')
    else:
        logdir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.FileHandler(pathlib.Path.home().joinpath(
                const.CERYLE_DIR,
                'logs',
                filename or dt.datetime.now().strftime('%Y%m%d-%H%M%S%f.log'))))

    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)8s %(name)s] %(message)s (%(pathname)s:%(lineno)d %(funcName)s)',
        handlers=handlers,
    )
