import ceryle.util as util

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

    def run(self, task_group):
        chain = self._deps_chain_map.get(task_group)
        return self._run(chain)

    def _run(self, chain):
        for c in chain.deps:
            res = self._run(c)
            if not res:
                return False
        return self._groups[chain.task_name].run()
