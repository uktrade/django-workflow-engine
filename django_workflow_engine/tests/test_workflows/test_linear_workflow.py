import pytest

from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import linear_workflow


@pytest.mark.django_db
def test_workflow_creation(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        linear_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 3

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]
