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
        return [
            "was_user_created",
        ], {}


class WasUserCreatedTask(Task):
    task_name = "was_user_created"
    auto = True

    def execute(self, task_info):
        user = User.objects.filter(
            first_name="Sam",
        ).first()

        if user:
            return ["notify_creator"], {}
        else:
            return [
                "remind_creator",
            ], {}


class RemindCreatorTask(Task):
    task_name = "remind_creator"
    auto = True

    def execute(self, task_info):
        logger.info("Please create user 'Sam'")
        return [
            "was_user_created",
        ], {}


class NotifyCreatorTask(Task):
    task_name = "notify_creator"
    auto = True

    def execute(self, task_info):
        logger.info("A User was created")
        return COMPLETE, {}


@pytest.mark.django_db(transaction=True)
def test_reminder_style_workflow(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="start_reminder",
                task_name="start_reminder",
                start=True,
                targets=["was_task_completed"],
            ),
            Step(
                step_id="was_user_created",
                task_name="was_user_created",
                targets=["remind_creator", "notify_creator"],
            ),
            Step(
                step_id="remind_creator",
                task_name="remind_creator",
                targets=[
                    "was_user_created",
                ],
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
    assert TaskRecord.objects.count() == 3

    task_record = TaskRecord.objects.last()
    executor.run_flow(
        user=test_user,
        task_uuids=[
            task_record.uuid,
        ],
    )

    assert TaskRecord.objects.count() == 5

    task_record = TaskRecord.objects.last()
    executor.run_flow(
        user=test_user,
        task_uuids=[
            task_record.uuid,
        ],
    )

    assert TaskRecord.objects.count() == 7

    correct_task_order = [
        "start_reminder",
        "was_user_created",
        "remind_creator",
        "was_user_created",
        "remind_creator",
        "was_user_created",
        "remind_creator",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]

    # Create user
    create_test_user(first_name="Sam", username="SamIAm")

    task_record = TaskRecord.objects.last()
    executor.run_flow(
        user=test_user,
        task_uuids=[
            task_record.uuid,
        ],
    )

    assert TaskRecord.objects.count() == 9

    correct_task_order.append("was_user_created")
    correct_task_order.append("notify_creator")

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]

    assert flow.is_complete
