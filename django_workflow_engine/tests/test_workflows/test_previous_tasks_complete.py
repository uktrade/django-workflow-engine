import pytest
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import previous_tasks_complete_workflow


@pytest.mark.django_db(transaction=True)
def test_previous_tasks_complete_workflow(settings):
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

    task, _ = executor.get_or_create_task_record(step=start)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 3
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert not end_task.done

    task, _ = executor.get_or_create_task_record(step=task_a)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 5
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert not end_task.done

    task, _ = executor.get_or_create_task_record(step=task_b)
    task.done = True
    task.save()

    executor.execute_step(user=test_user, step=end)

    assert flow.tasks.count() == 7
    end_task = flow.tasks.filter(step_id=end.step_id).last()
    assert end_task.done
