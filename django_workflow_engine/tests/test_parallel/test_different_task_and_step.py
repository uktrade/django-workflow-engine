import pytest

from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import set_up_flow


class DifferentTaskAndStepTask(Task):
    task_name = "different_task_and_step_task"
    auto = True

    def execute(self, task_info):
        return None, True


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="first",
                task_name="different_task_and_step_task",
                start=True,
                targets=["second"],
            ),
            Step(
                step_id="second",
                task_name="different_task_and_step_task",
                targets=["last"],
            ),
            Step(
                step_id="last",
                task_name="different_task_and_step_task",
                targets=COMPLETE,
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 3

    correct_task_order = [
        "first",
        "second",
        "last",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]
