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
    assert TaskRecord.objects.count() == 3
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    executor.run_flow(user=test_user)

    assert not flow.is_complete
    assert TaskRecord.objects.count() == 4
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    executor.run_flow(user=test_user)

    assert not flow.is_complete
    assert TaskRecord.objects.count() == 5
    assert TaskRecord.objects.filter(executed_at__isnull=True).count() == 1

    correct_task_order = [
        "start_reminder",
        "was_user_created",
        "remind_creator",
        "was_user_created",
        "remind_creator",
    ]

    task_order = [task_record.step_id for task_record in TaskRecord.objects.all()]
    assert task_order == correct_task_order

    # Create "Sam" user
    UserFactory(first_name="Sam")

    # Execute the flow until it completes
    while not flow.is_complete:
        executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 7

    correct_task_order.append("was_user_created")
    correct_task_order.append("notify_creator")

    task_order = [task_record.step_id for task_record in TaskRecord.objects.all()]
    assert task_order == correct_task_order
