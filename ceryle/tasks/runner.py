import logging
import ceryle.util as util

from ceryle.tasks import TaskDefinitionError, TaskIOError
from ceryle.tasks.resolver import DependencyResolver
from ceryle.tasks.task import TaskGroup

logger = logging.getLogger(__name__)


class TaskRunner:
    def __init__(self, task_groups):
        util.assert_type(task_groups, list)
        for g in task_groups:
            util.assert_type(g, TaskGroup)

        resolver = DependencyResolver(dict([(g.name, [*g.dependencies]) for g in task_groups]))
        resolver.validate()
        self._deps_chain_map = resolver.deps_chain_map()
        self._groups = dict([(g.name, g) for g in task_groups])

    def run(self, task_group, dry_run=False):
        chain = self._deps_chain_map.get(task_group)
        if chain is None:
            raise TaskDefinitionError(f'task {task_group} is not defined')
        return self._run(chain, dry_run=dry_run)[0]

    def _run(self, chain, dry_run=False, register={}):
        r = dict(register)
        for c in chain.deps:
            res, r = self._run(c, dry_run=dry_run, register=r)
            if not res:
                return False, r
        return self._run_group(self._groups[chain.task_name], dry_run=dry_run, register=r)

    def _run_group(self, tg, dry_run=False, register={}):
        logger.info(f'running task group {tg.name}')
        r = dict(register)
        for t in tg.tasks:
            if t.input_key and t.input_key not in r:
                raise TaskIOError(f'{t.input_key} is required by a task in {tg.name}, but not registered')
            if not t.run(dry_run=dry_run, inputs=r.get(t.input_key, [])):
                return False, r
            if t.stdout_key:
                r.update({t.stdout_key: t.stdout()})
            if t.stderr_key:
                r.update({t.stderr_key: t.stderr()})
        return True, r
