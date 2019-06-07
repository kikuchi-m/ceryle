from ceryle.tasks.resolver import DependencyResolver
from ceryle.tasks.task import TaskGroup
from ceryle.util import assert_type


class TaskRunner:
    def __init__(self, task_groups):
        assert_type(task_groups, list)
        for g in task_groups:
            assert_type(g, TaskGroup)

        resolver = DependencyResolver(_deps_map(task_groups))
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


def _deps_map(task_groups):
    deps_map = {}
    for g in task_groups:
        deps_map[g.name] = [*g.dependencies]
    return deps_map
