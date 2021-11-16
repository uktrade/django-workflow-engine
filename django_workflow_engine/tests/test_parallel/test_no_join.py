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
        return ["finish_up_a"], {}


class TaskB(Task):
    task_name = "task_b"
    auto = True

    def execute(self, task_info):
        return ["finish_up_b"], {}


class FinishTaskA(Task):
    task_name = "finish_up_a"
    auto = True

    def execute(self, task_info):
        return None, {}


class FinishTaskB(Task):
    task_name = "finish_up_b"
    auto = True

    def execute(self, task_info):
        return None, {}


@pytest.mark.django_db(transaction=True)
def test_parallel_path_no_join_workflow(settings):
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
                target=["finish_up_a"],
            ),
            Step(
                step_id="task_b",
                task_name="task_b",
                target=["finish_up_b"],
            ),
            Step(
                step_id="finish_up_a",
                task_name="finish_up_a",
                target=None,
            ),
            Step(
                step_id="finish_up_b",
                task_name="finish_up_b",
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
        "finish_up_a",
        "task_b",
        "finish_up_b",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]
