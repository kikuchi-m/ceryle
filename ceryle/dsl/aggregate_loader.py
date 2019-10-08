import ceryle
import ceryle.util as util


class AggregateTaskFileLoader:
    def __init__(self, files, extensions=[], additional_args={}):
        self._files = util.assert_type(files, list)[:]
        self._extensions = util.assert_type(extensions, list)[:]
        self._additional_args = additional_args.copy()

    def load(self):
        tasks = {}
        default = None
        lvars = {}
        for f in self._extensions:
            x = ceryle.ExtensionLoader(f).load(
                local_vars=lvars.copy(),
                additional_args=self._additional_args)
            lvars.update(x)
        for f in self._files:
            d = ceryle.TaskFileLoader(f).load(
                local_vars=lvars.copy(),
                additional_args=self._additional_args)
            for t in d.tasks:
                if t.name in tasks:
                    util.print_out(f'warn: {t.name} is overwritten')
                tasks.update({t.name: t})
            if d.default_task:
                default = d.default_task
        return ceryle.TaskDefinition(list(tasks.values()), default)


def load_task_files(files, extensions, additional_args={}):
    return AggregateTaskFileLoader(files, extensions=extensions, additional_args=additional_args).load()
