import logging

import pytest

from django_workflow_engine.models import TaskStatus
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
    assert TaskStatus.objects.count() == 3
    assert TaskStatus.objects.filter(done=True).count() == 1

    executor.run_flow(user=test_user)

    assert not flow.is_complete
    assert TaskStatus.objects.count() == 3
    assert TaskStatus.objects.filter(done=True).count() == 2

    executor.run_flow(user=test_user)

    assert not flow.is_complete
    assert TaskStatus.objects.count() == 3
    assert TaskStatus.objects.filter(done=True).count() == 2

    correct_task_order = [
        "start_reminder",
        "was_user_created",
        "remind_creator",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order

    # Create "Sam" user
    UserFactory(first_name="Sam")

    # Execute the flow until it completes
    while not flow.is_complete:
        executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 4

    correct_task_order.append("notify_creator")

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order
