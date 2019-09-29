import copy
import logging
import pickle

import ceryle.util as util
from ceryle import IllegalOperation
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
        self._run_cache = None

    def run(self, task_group, dry_run=False):
        chain = self._deps_chain_map.get(task_group)
        if chain is None:
            raise TaskDefinitionError(f'task {task_group} is not defined')
        self._run_cache = RunCache(task_group)
        return self._run(chain, dry_run=dry_run)[0]

    def get_cache(self):
        if self._run_cache is None:
            raise IllegalOperation('could not get cache before running')
        return self._run_cache

    def _run(self, chain, dry_run=False, register={}):
        reg = None
        for c in chain.deps:
            res, reg = self._run(c, dry_run=dry_run, register=register)
            if not res:
                return False, reg
        try:
            res, reg = self._run_group(self._groups[chain.task_name], dry_run=dry_run, register=reg or register)
            self._run_cache.add_result((chain.task_name, res and not dry_run))
            self._run_cache.update_register(reg)
        except Exception:
            self._run_cache.add_result((chain.task_name, False))
            raise

        return res, reg

    def _run_group(self, tg, dry_run=False, register={}):
        logger.info(f'running task group {tg.name}')
        r = copy.deepcopy(register)
        for t in tg.tasks:
            inputs = []
            if t.input_key:
                if isinstance(t.input_key, str):
                    logger.debug(f'read {tg.name}.{t.input_key} from register')
                    inputs = util.getin(r, tg.name, t.input_key)
                else:
                    logger.debug(f'read {".".join(t.input_key)} from register')
                    inputs = util.getin(r, *t.input_key)
                if inputs is None:
                    raise TaskIOError(f'{t.input_key} is required by a task in {tg.name}, but not registered')
            if not t.run(dry_run=dry_run, inputs=inputs):
                return False, r
            if t.stdout_key:
                logger.debug(f'register {t.stdout_key}')
                _update_register(r, tg.name, t.stdout_key, t.stdout())
            if t.stderr_key:
                logger.debug(f'register {t.stderr_key}')
                _update_register(r, tg.name, t.stderr_key, t.stderr())
        return True, r


def _update_register(register, group, key, std):
    tg_r = util.getin(register, group, default={})
    tg_r.update({key: std})
    register.update({group: tg_r})


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
        return copy.deepcopy(self._register)

    def add_result(self, result):
        util.assert_type(result, tuple, list)
        self._results.append((
            util.assert_type(result[0], str),
            util.assert_type(result[1], bool),
        ))

    def update_register(self, register):
        self._register = copy.deepcopy(util.assert_type(register, dict))

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
