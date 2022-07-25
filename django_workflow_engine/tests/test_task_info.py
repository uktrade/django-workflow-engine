import pytest
from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.tests.utils import set_up_flow


class TaskInfoTask(Task):
    task_name = "task_info_task"
    auto = True

    def execute(self, task_info):
        print("Task name: ", task_info["task_name"])
        return [], True


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="test_task_1",
                task_name="task_info_task",
                start=True,
                targets=["test_task_2"],
                task_info={
                    "task_name": "Test task 1",
                },
            ),
            Step(
                step_id="test_task_2",
                task_name="task_info_task",
                targets=["test_task_3"],
                task_info={
                    "task_name": "Test task 2",
                },
            ),
            Step(
                step_id="test_task_3",
                task_name="task_info_task",
                targets=COMPLETE,
                task_info={
                    "task_name": "Test task 3",
                },
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)
