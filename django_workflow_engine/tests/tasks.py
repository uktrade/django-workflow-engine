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
        return [], True


class PauseTask(Task):
    task_name = "pause_task"
    auto = True

    def execute(self, task_info):
        return [], False


class ErrorTask(Task):
    task_name = "error_task"
    auto = True

    def execute(self, task_info):
        raise Exception("Error")


class SelfReferencingPauseTask(Task):
    task_name = "self_ref_pause_task"
    auto = True

    def execute(self, task_info):
        return ["self_ref_pause_task"], False


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


class WasUserCreatedTaskA(Task):
    task_name = "was_user_created_task_a"
    auto = True

    def execute(self, task_info):
        user = User.objects.filter(
            first_name="Sam",
        ).first()

        if not user:
            return ["task_a_remind_creator"], False

        return ["task_a_notify_creator"], True


class WasUserCreatedTaskB(Task):
    task_name = "was_user_created_task_b"
    auto = True

    def execute(self, task_info):
        user = User.objects.filter(
            first_name="Sam",
        ).first()

        if not user:
            return ["task_b_remind_creator"], False

        return ["task_b_notify_creator"], True


class InvalidTargetTask(Task):
    task_name = "invalid_target_task"
    auto = True

    def execute(self, task_info):
        return ["not_a_real_step_id"], True
