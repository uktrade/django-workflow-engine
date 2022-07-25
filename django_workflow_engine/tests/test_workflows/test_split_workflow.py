import pytest
from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import split_workflow


@pytest.mark.django_db()
def test_parallel_path_no_join_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        split_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 5

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
        "finish_task_a",
        "finish_task_b",
    ]

    task_order = [task_record.step_id for task_record in TaskRecord.objects.all()]
    assert task_order == correct_task_order
