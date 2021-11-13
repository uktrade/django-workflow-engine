from django_workflow_engine import Workflow, Step, Task
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow

from django_workflow_engine.tests.utils import create_test_user


class TestTask(Task, input="test_task"):
    auto = True

    def execute(self, task_info):
        return None, {}


def test_workflow_creation():
    test_user = create_test_user()

    test_workflow = Workflow(
        name="leaving",
        steps=[
            Step(
                step_id="test_task",
                task_name="test_task",
                start=True,
                target=None,
            ),
        ]
    )

    flow = Flow.objects.create(
        workflow_name="Test Workflow",
        flow_name="test_flow",
        executed_by=test_user,
    )
    flow.save()

    executor = WorkflowExecutor(flow)
    executor.run_flow(user=test_user)


def test_only_group_member_can_execute():
    pass
    # try:
    #     executor.run_flow(user=test_user)
    # except WorkflowNotAuthError as e:
    #     raise PermissionDenied(f"{e}")
