import pytest
from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.tests.utils import set_up_flow


class BasicTask(Task):
    task_name = "basic_task"
    auto = True

    def execute(self, task_info):
        return None, {}, task_info["task_finished"]


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="test_task",
                task_name="basic_task",
                start=True,
                targets=COMPLETE,
                task_info={
                    "task_finished": True,
                },
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)
