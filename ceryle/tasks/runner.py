import logging
import pickle

import ceryle.util as util
from ceryle import IllegalOperation
from ceryle.tasks import TaskDefinitionError
from ceryle.tasks.task import copy_register
from ceryle.tasks.resolver import DependencyResolver

logger = logging.getLogger(__name__)


class TaskRunner:
    def __init__(self, task_groups):
        self._resolver = DependencyResolver(task_groups)
        self._resolver.validate()
        self._run_cache = None
        self._sw = util.StopWatch()

    def run(self, task_group, dry_run=False, last_run=None):
        chain = self._resolver.deps_chain_map().get(util.assert_type(task_group, str))
        if chain is None:
            print_similar_task_groups(self._resolver.find_similar(task_group))
            raise TaskDefinitionError(f'task {task_group} is not defined')
        self._run_cache = RunCache(task_group)
        if last_run is not None:
            logger.debug(f'last run: {last_run}')
        last_execution = LastExecution(last_run)
        if last_execution.task_name != task_group:
            last_execution.stop()
        self._sw.start()
        res, _ = self._run(chain, dry_run=dry_run, last_execution=last_execution)
        return res

    def get_cache(self):
        if self._run_cache is None:
            raise IllegalOperation('could not get cache before running')
        return self._run_cache

    def _run(self, chain, dry_run=False, register={}, last_execution=None):
        reg = copy_register(register)
        for c in chain.deps:
            res, reg = self._run(c, dry_run=dry_run, register=reg, last_execution=last_execution)
            if not res:
                return False, reg

        tg = chain.root
        if tg.allow_skip and self._run_cache.has(chain.task_name):
            logger.info(f'skipping {chain} since it has already run')
            return True, register

        if last_execution.check_skip(chain.task_name):
            logger.info(f'skipping {chain} since succeeded last run')
            util.print_out(f'skipping {chain.task_name}')
            self._run_cache.add_result(last_execution.current_result())
            last_execution.forward()
            return True, last_execution.register
        else:
            last_execution.stop()

        try:
            util.print_out(f'running task group {chain.task_name}', level=logging.INFO)
            res, reg = tg.run(dry_run=dry_run, register=reg or register)
            self._sw.elapse()
            util.print_out(f'finished {chain.task_name} {self._sw.str_last_lap()}', level=logging.INFO)
        except Exception:
            self._run_cache.add_result((chain.task_name, False))
            raise
        self._run_cache.add_result((chain.task_name, res and not dry_run))
        self._run_cache.update_register(reg)
        return res, reg


def print_similar_task_groups(similars):
    names = [c.task_name for c in similars]
    if names:
        tasks = ', '.join(names)
        logger.debug(f'simer tasks: [{tasks}]')
        msg = [
            'similar task groups are',
            *[util.indent_s(t, 4) for t in names[:5]]
        ]
        if len(names) > 5:
            msg.append(util.indent_s('...', 4))
        util.print_out(*msg)


class RunCache:
    def __init__(self, task_name):
        self._task_name = util.assert_type(task_name, str)
        self._results = []
        self._register = {}

    @property
    def task_name(self):
        return self._task_name

    @property
    def results(self):
        return [*self._results]

    @property
    def register(self):
        return copy_register(self._register)

    def add_result(self, result):
        util.assert_type(result, tuple, list)
        self._results.append((
            util.assert_type(result[0], str),
            util.assert_type(result[1], bool),
        ))

    def has(self, task_group):
        return task_group in [n for n, _ in self._results]

    def update_register(self, register):
        self._register = copy_register(util.assert_type(register, dict))

    def save(self, path):
        with open(path, 'wb') as fp:
            pickle.dump(self, fp, protocol=0)

    @staticmethod
    def load(path):
        try:
            with open(path, 'rb') as fp:
                return pickle.load(fp)
        except Exception as e:
            logger.warn(f'failed to load run cache: {path}')
            logger.warn(e)
            return None

    def __str__(self):
        res = ', '.join([f'({r[0]}, {r[1]})' for r in self._results])
        return f'RunCache({self._task_name}, results={res}'


class LastExecution:
    def __init__(self, run_cache):
        self._run_cache = util.assert_type(run_cache, None, RunCache)
        self._results = run_cache and run_cache.results or []
        self._index = 0

    def has_current(self):
        return self._index < len(self._results)

    def current_result(self):
        if not self.has_current():
            raise IllegalOperation('no result exists')
        return self._results[self._index]

    def check_skip(self, task_group):
        if self.has_current():
            g, r = self._results[self._index]
            return g == task_group and r
        return False

    def forward(self):
        self._index += 1

    def stop(self):
        self._index = len(self._results)

    @property
    def register(self):
        return self._run_cache and self._run_cache.register or {}

    @property
    def task_name(self):
        return self._run_cache and self._run_cache.task_name
