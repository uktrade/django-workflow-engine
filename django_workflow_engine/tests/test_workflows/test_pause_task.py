import pytest
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import pause_task_workflow


@pytest.mark.django_db(transaction=True)
def test_pause_task_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        pause_task_workflow,
    )

    with pytest.raises(Exception):
        executor.run_flow(user=test_user)

    flow.refresh_from_db()
    assert flow.tasks.count() == 2
    assert not flow.is_complete

    with pytest.raises(Exception):
        executor.run_flow(user=test_user)

    flow.refresh_from_db()
    assert flow.tasks.count() == 2
    assert not flow.is_complete

    with pytest.raises(Exception):
        executor.run_flow(user=test_user)

    flow.refresh_from_db()
    assert flow.tasks.count() == 2
    assert not flow.is_complete
