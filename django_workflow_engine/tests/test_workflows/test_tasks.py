from unittest import mock

import pytest

from django_workflow_engine.models import TaskStatus
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import invalid_task_target_workflow


@mock.patch("django_workflow_engine.executor.logger.exception")
@pytest.mark.django_db
def test_invalid_target(mock_exception, settings):
    flow, executor, test_user = set_up_flow(
        settings,
        invalid_task_target_workflow,
    )
    executor.run_flow(user=test_user)

    # Check that a WorkflowError was logged.
    mock_exception.assert_called_once()
    assert (
        str(mock_exception.call_args[0][0])
        == "Step 'not_a_real_step_id' not found in workflow"
    )

    assert TaskStatus.objects.count() == 2

    correct_task_order = [
        "start",
        "task_a",
    ]

    task_order = [task_status.step_id for task_status in TaskStatus.objects.all()]
    assert task_order == correct_task_order
