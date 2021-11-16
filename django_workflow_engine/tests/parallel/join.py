import pytest

from django_workflow_engine import Workflow, Step, Task
from django_workflow_engine.models import TaskRecord

from django_workflow_engine.tests.utils import set_up_flow


class StartTask(Task):
    task_name = "start"
    auto = True

    def execute(self, task_info):
        return ["task_a", "task_b"], {}


class TaskA(Task):
    task_name = "task_a"
    auto = True

    def execute(self, task_info):
        return ["meet_up", ], {}


class TaskB(Task):
    task_name = "task_b"
    auto = True

    def execute(self, task_info):
        return ["meet_up", ], {}


class MeetUp(Task):
    task_name = "meet_up"
    auto = True

    def execute(self, task_info):
        return None, {}


@pytest.mark.django_db
def test_parallel_path_join_up_workflow(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="start",
                task_name="start",
                start=True,
                target=["task_a", "task_b"],
            ),
            Step(
                step_id="task_a",
                task_name="task_a",
                target=["meet_up"],
            ),
            Step(
                step_id="task_b",
                task_name="task_b",
                target=["meet_up"],
            ),
            Step(
                step_id="meet_up",
                task_name="meet_up",
                target=None,
            ),
        ]
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 5

    correct_task_order = [
        "start",
        "task_a",
        "meet_up",
        "task_b",
        "meet_up",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]
