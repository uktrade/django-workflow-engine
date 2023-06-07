import pytest

from django_workflow_engine.models import TaskStatus
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import linear_workflow


@pytest.mark.django_db
def test_workflow_creation(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        linear_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 3

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order


@pytest.mark.django_db()
def test_with_error_workflow(settings):
    linear_workflow.steps[1].task_name = "error_task"

    flow, executor, test_user = set_up_flow(
        settings,
        linear_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 2
    assert TaskStatus.objects.filter(done=True).count() == 1

    correct_task_order = [
        "start",
        "task_a",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order
