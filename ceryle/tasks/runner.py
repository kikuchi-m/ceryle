import ceryle.util as util

from ceryle.tasks import TaskDefinitionError
from ceryle.tasks.resolver import DependencyResolver
from ceryle.tasks.task import TaskGroup


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
        return self._run(chain, dry_run=dry_run)

    def _run(self, chain, dry_run=False):
        for c in chain.deps:
            res = self._run(c, dry_run=dry_run)
            if not res:
                return False
        return self._run_group(self._groups[chain.task_name], dry_run=dry_run)

    def _run_group(self, tg, dry_run=False):
        for t in tg.tasks:
            if not t.run(dry_run=dry_run):
                return False
        return True
