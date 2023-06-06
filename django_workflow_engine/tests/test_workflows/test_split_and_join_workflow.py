import pytest

from django_workflow_engine.models import TaskStatus
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import split_and_join_workflow


@pytest.mark.django_db(transaction=True)
def test_parallel_path_join_up_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        split_and_join_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 4

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
        "task_c",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order


@pytest.mark.django_db(transaction=True)
def test_parallel_path_join_up_with_error_workflow(settings):
    split_and_join_workflow.steps[1].task_name = "error_task"

    flow, executor, test_user = set_up_flow(
        settings,
        split_and_join_workflow,
    )
    executor.run_flow(user=test_user)
    executor.run_flow(user=test_user)

    assert TaskStatus.objects.count() == 4
    assert TaskStatus.objects.filter(done=True).count() == 3

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
        "task_c",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order
