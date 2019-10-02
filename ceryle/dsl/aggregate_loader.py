import ceryle
import ceryle.util as util


class AggregateTaskFileLoader:
    def __init__(self, files, additional_args={}):
        self._files = util.assert_type(files, list)[:]
        self._additional_args = additional_args.copy()

    def load(self):
        tasks = {}
        default = None
        gvars = {}
        lvars = {}
        for f in self._files:
            d = ceryle.TaskFileLoader(f).load(
                global_vars=gvars,
                local_vars=lvars,
                additional_args=self._additional_args)
            for t in d.tasks:
                if t.name in tasks:
                    util.print_out(f'warn: {t.name} is overwritten')
                tasks.update({t.name: t})
            default = d.default_task
            gvars = d.global_vars
            lvars = d.local_vars
        return ceryle.dsl.loader.TaskDefinition(list(tasks.values()), default)


def load_task_files(files, additional_args={}):
    return AggregateTaskFileLoader(files, additional_args=additional_args).load()
