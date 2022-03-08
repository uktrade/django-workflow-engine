import logging

import pytest
from django.contrib.auth.models import User

from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import create_test_user, set_up_flow

logger = logging.getLogger("test")


class StartReminderTask(Task):
    task_name = "start_reminder"
    auto = True

    def execute(self, task_info):
        return ["was_user_created"], True


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


class RemindCreatorTask(Task):
    task_name = "remind_creator"
    auto = True

    def execute(self, task_info):
        logger.info("Please create user 'Sam'")
        return ["was_user_created"], True


class NotifyCreatorTask(Task):
    task_name = "notify_creator"
    auto = True

    def execute(self, task_info):
        logger.info("A User was created")
        return COMPLETE, True


@pytest.mark.django_db(transaction=True)
def test_reminder_style_workflow(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="start_reminder",
                task_name="start_reminder",
                start=True,
                targets=["was_user_created"],
            ),
            Step(
                step_id="was_user_created",
                task_name="was_user_created",
                targets=["remind_creator", "notify_creator"],
            ),
            Step(
                step_id="remind_creator",
                task_name="remind_creator",
                targets=["was_user_created"],
                break_flow=True,
            ),
            Step(
                step_id="notify_creator",
                task_name="notify_creator",
                targets=[COMPLETE],
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )

    executor.run_flow(user=test_user)

    assert not flow.is_complete
    assert TaskRecord.objects.count() == 4
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 6
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 8
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    correct_task_order = [
        "start_reminder",
        "was_user_created",
        "remind_creator",
        "was_user_created",
        "remind_creator",
        "was_user_created",
        "remind_creator",
        "was_user_created",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]

    # Create user
    create_test_user(first_name="Sam", username="SamIAm")

    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 9

    correct_task_order.append("notify_creator")

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]

    assert flow.is_complete
