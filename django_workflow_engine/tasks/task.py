"""Django workflow Task.

A task is an instance of a django_workflow_engine.dataclasses.Step
"""


class TaskError(Exception):
    def __init__(self, message, context):
        self.message = message
        self.context = context


class Task:
    tasks = {}
    template = None

    def __init__(self, user, task_record, flow):
        self.user = user
        self.task_record = task_record
        self.flow = flow

    def setup(self, task_info):
        pass

    def execute(self, task_info):
        raise NotImplementedError

    def log(self, message):
        self.task_record.log.create(message=message)

    def __init_subclass__(cls, /, input, **kwargs):  # noqa
        super().__init_subclass__(**kwargs)
        cls.tasks[input] = cls
