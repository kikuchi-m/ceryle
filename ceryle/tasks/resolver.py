import ceryle.util as util

from . import TaskDependencyError


class DependencyResolver:
    def __init__(self, deps_map):
        self._deps_map = dict(deps_map)
        self._deps_chain_map = None

    def validate(self):
        if self._deps_chain_map is None:
            chain_map = _construct_chain_map(self._deps_map)
            self._deps_chain_map = _reconstruct(chain_map)

    def deps_chain_map(self):
        """
        form: { <name: str>: <chain: DependencyChain> }
        """

        self.validate()
        return dict(self._deps_chain_map)


def _construct_chain_map(deps_map):
    dcm = {}
    for t, deps in deps_map.items():
        c = dcm.get(t)
        if c is None:
            c = DependencyChain(t)
            dcm[t] = c
        for t_dep in deps:
            t_dep_c = dcm.get(t_dep, DependencyChain(t_dep))
            if t_dep not in deps_map:
                raise TaskDependencyError(f'task {t_dep} depended by {t} is not defined')
            if t == t_dep:
                raise TaskDependencyError(f'cyclic dependency was found: {t} -> {t_dep}')
            if t_dep_c.depends_on(c):
                chain_str = ' -> '.join([t, *[c1.task_name for c1 in t_dep_c.get_chain(c, include_self=True)]])
                raise TaskDependencyError(f'cyclic dependency was found: {chain_str}')

            dcm[t_dep] = t_dep_c
            c.add_dependency(t_dep_c)
    return dcm


def _reconstruct(chain_map):
    reconstructed = {}
    for t, chain in chain_map.items():
        c = DependencyChain(t)
        for d in chain.deps:
            c.add_dependency(d)
        reconstructed[t] = c
    return reconstructed


class DependencyChain:
    def __init__(self, task_name):
        self._task_name = task_name
        self._deps = []

    def add_dependency(self, dep):
        util.assert_type(dep, DependencyChain)
        if not self.depends_on(dep):
            self._deps = [*self._deps, dep]
            return True
        return False

    def depends_on(self, dep):
        util.assert_type(dep, DependencyChain)
        for d in self._deps:
            if dep == d or d.depends_on(dep):
                return True
        return False

    def get_chain(self, dep, include_self=False):
        util.assert_type(dep, DependencyChain)
        chain = self._get_chain([], self._deps, dep)
        if include_self:
            return [self, *chain]
        return chain

    def _get_chain(self, chain, deps, dep):
        for d in deps:
            if d == dep:
                return [d]
            c = self._get_chain(chain, d._deps, dep)
            if c:
                return [d, *c]
        return chain

    @property
    def task_name(self):
        return self._task_name

    @property
    def deps(self):
        return [*self._deps]

    def __str__(self):
        return f'DependencyChain({self.task_name}, {[d.task_name for d in self._deps]})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, DependencyChain):
            return self.task_name == other.task_name and self._deps == other._deps
        return False


def dump_chain(dep_chain):
    def add_lines(deps, i, lines):
        for d in deps:
            lines.append(d.task_name.rjust(len(d.task_name) + i * 4))
            add_lines(d.deps, i + 1, lines)
        return lines
    return '\n'.join(add_lines(dep_chain.deps, 1, [f'{dep_chain.task_name}']))
