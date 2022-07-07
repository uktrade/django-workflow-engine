import logging

import pytest
from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.factories import UserFactory
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import reminder_workflow

logger = logging.getLogger("test")


@pytest.mark.django_db(transaction=True)
def test_reminder_style_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        reminder_workflow,
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

    # Create "Sam" user
    UserFactory(first_name="Sam")

    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 9

    correct_task_order.append("notify_creator")

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]

    assert flow.is_complete
