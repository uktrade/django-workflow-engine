import pytest

from django_workflow_engine import Workflow, Step, Task
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.models import TaskRecord
from django_workflow_engine import COMPLETE


class BasicTask(Task):
    task_name = "basic_task"
    auto = True

    def execute(self, task_info):
        return None, {}


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="first",
                task_name="basic_task",
                start=True,
                targets=["second", ],
            ),
            Step(
                step_id="second",
                task_name="basic_task",
                start=True,
                targets=["last", ],
            ),
            Step(
                step_id="last",
                task_name="basic_task",
                start=True,
                targets=COMPLETE,
            ),
        ]
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
