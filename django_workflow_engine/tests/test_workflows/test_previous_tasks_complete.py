from unittest import mock

import pytest

from django_workflow_engine.tests.tasks import BasicTask
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import (
    previous_tasks_complete_failure_workflow,
    previous_tasks_complete_workflow,
)


@pytest.mark.django_db(transaction=True)
def test_previous_tasks_complete_task(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        previous_tasks_complete_workflow,
    )

    start = flow.workflow.get_step("start")
    task_a = flow.workflow.get_step("task_a")
    task_b = flow.workflow.get_step("task_b")
    end = flow.workflow.get_step("task_c")

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 1
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert not end_task.done

    task, _ = executor.get_or_create_task_status(step=start)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 2
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert not end_task.done

    task, _ = executor.get_or_create_task_status(step=task_a)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 3
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert not end_task.done

    task, _ = executor.get_or_create_task_status(step=task_b)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 4
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert end_task.done


@pytest.mark.django_db(transaction=True)
def test_previous_tasks_complete_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        previous_tasks_complete_workflow,
    )

    executor.run_flow(user=test_user)

    assert flow.tasks.count() == 4
    end_task = flow.tasks.filter(step_id="task_c").last()
    assert end_task.done


@mock.patch(
    "django_workflow_engine.tests.tasks.PauseTask.execute", return_value=([], False)
)
@pytest.mark.django_db(transaction=True)
def test_previous_tasks_complete_failure_workflow(mock_execute, settings):
    flow, executor, test_user = set_up_flow(
        settings,
        previous_tasks_complete_failure_workflow,
    )

    executor.run_flow(user=test_user)

    assert flow.tasks.count() == 4
    end_task = flow.tasks.filter(step_id="task_c").last()
    assert not end_task.done

    mock_execute.return_value = ([], True)

    while not flow.tasks.filter(step_id="task_c", done=True).exists():
        executor.run_flow(user=test_user)

    assert flow.tasks.count() == 4
    end_task = flow.tasks.filter(step_id="task_c").last()
    assert end_task.done
