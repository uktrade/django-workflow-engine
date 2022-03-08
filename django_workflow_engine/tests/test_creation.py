import pytest

from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.tests.utils import set_up_flow


class WorkflowCreationTestTask(Task):
    task_name = "workflow_createion_test_task"
    auto = True

    def execute(self, task_info):
        return None, True


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="test_task",
                task_name="workflow_createion_test_task",
                start=True,
                targets=COMPLETE,
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)


def test_only_group_member_can_execute():
    # TODO
    pass
