from django.contrib.auth import get_user_model
from django_workflow_engine.tasks.task import Task

User = get_user_model()

"""
Test Task definitions

These are used in the test Workflows defined in "/django_workflow_engine/tests/workflows.py"
"""


class BasicTask(Task):
    task_name = "basic_task"
    auto = True

    def execute(self, task_info):
        return None, True


class WasUserCreatedTask(Task):
    task_name = "was_user_created"
    auto = True

    def execute(self, task_info):
        user = User.objects.filter(
            first_name="Sam",
        ).first()

        if not user:
            return ["remind_creator"], False

        return ["notify_creator"], True
