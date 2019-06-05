
class TaskDependencyError(Exception):
    def __init__(self, messame):
        super(TaskDependencyError, self).__init__(messame)
