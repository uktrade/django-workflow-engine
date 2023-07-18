import pytest

from django_workflow_engine.models import TaskStatus
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import invalid_task_target_workflow


@pytest.mark.django_db
def test_invalid_target(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        invalid_task_target_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 2

    correct_task_order = [
        "start",
        "task_a",
        # Task B fails to run because it's target is invalid
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order
