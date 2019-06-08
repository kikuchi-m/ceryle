class TaskFileError(Exception):
    def __init__(self, message):
        super(TaskFileError, self).__init__(message)
