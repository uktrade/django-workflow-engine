from unittest import mock

import pytest

from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import (
    pause_task_workflow,
    self_ref_pause_task_workflow,
)

PAUSE_WORKFLOWS = [pause_task_workflow, self_ref_pause_task_workflow]


@mock.patch("django_workflow_engine.tests.tasks.PauseTask.execute")
@pytest.mark.django_db(transaction=True)
def test_pause_task_workflows(mock_execute, settings):
    for pause_workflow in PAUSE_WORKFLOWS:
        mock_execute.return_value = ([], False)

        flow, executor, test_user = set_up_flow(
            settings,
            pause_workflow,
        )

        executor.run_flow(user=test_user)

        flow.refresh_from_db()
        assert flow.tasks.count() == 2
        assert not flow.is_complete

        executor.run_flow(user=test_user)

        flow.refresh_from_db()
        assert flow.tasks.count() == 2
        assert not flow.is_complete

        executor.run_flow(user=test_user)

        flow.refresh_from_db()
        assert flow.tasks.count() == 2
        assert not flow.is_complete

        mock_execute.return_value = ([], True)

        executor.run_flow(user=test_user)

        flow.refresh_from_db()
        assert flow.tasks.count() == 3
        assert flow.is_complete

        executor.run_flow(user=test_user)

        flow.refresh_from_db()
        assert flow.tasks.count() == 3
        assert flow.is_complete
