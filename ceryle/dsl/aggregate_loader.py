import ceryle


class AggregateTaskFileLoader:
    def __init__(self, files):
        self._files = list(files)

    def load(self):
        tasks = {}
        default = None
        gvars = {}
        lvars = {}
        for f in self._files:
            d = ceryle.TaskFileLoader(f).load(global_vars=gvars, local_vars=lvars)
            tasks.update([(d.name, d) for d in d.tasks])
            default = d.default_task
            gvars = d.global_vars
            lvars = d.local_vars
        return ceryle.dsl.loader.TaskDefinition(list(tasks.values()), default)


def load_task_files(files):
    return AggregateTaskFileLoader(files).load()
