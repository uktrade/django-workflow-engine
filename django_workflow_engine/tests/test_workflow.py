import pytest

from django.conf import settings

from django_workflow_engine import Workflow, Step, Task
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow, TaskRecord

from django_workflow_engine.tests.utils import create_test_user


class BasicTask(Task):
    task_name = "test_task"
    auto = True

    def execute(self, task_info):
        print("Executed...")
        return None, {}


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_user = create_test_user()

    test_workflow = Workflow(
        name="test_workflow_1",
        steps=[
            Step(
                step_id="test_task",
                task_name="test_task",
                start=True,
                target=None,
            ),
        ]
    )

    settings.DJANGO_WORKFLOWS = {
        "test_workflow_1": test_workflow,
    }

    flow = Flow.objects.create(
        workflow_name="test_workflow_1",
        flow_name="test_flow",
        executed_by=test_user,
    )
    flow.save()

    executor = WorkflowExecutor(flow)
    executor.run_flow(user=test_user)


class Branch(Task):
    task_name = "branch_test"
    auto = True

    def execute(self, task_info):
        # print("Branching...")
        return ["task_a", "task_b"], {}


class BranchedA(Task):
    task_name = "branched_a_test"
    auto = True

    def execute(self, task_info):
        # print("Branched A...")
        return ["finish_up_a", ], {}


class BranchedB(Task):
    task_name = "branched_b_test"
    auto = True

    def execute(self, task_info):
        # print("Branched B...")
        return ["finish_up_b", ], {}


class FinishA(Task):
    task_name = "finish_up_a"
    auto = True

    def execute(self, task_info):
        # print("Finish up a...")
        return None, {}


class FinishB(Task):
    task_name = "finish_up_b"
    auto = True

    def execute(self, task_info):
        # print("Finish up b...")
        return None, {}


@pytest.mark.django_db
def test_multi_path_workflow(settings):
    test_user = create_test_user()

    test_workflow = Workflow(
        name="test_workflow_1",
        steps=[
            Step(
                step_id="start",
                task_name="branch_test",
                start=True,
                target=["task_a", "task_b"],
            ),
            Step(
                step_id="task_a",
                task_name="branched_a_test",
                target=["finish_up_a"],
            ),
            Step(
                step_id="task_b",
                task_name="branched_b_test",
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

    settings.DJANGO_WORKFLOWS = {
        "test_workflow_1": test_workflow,
    }

    flow = Flow.objects.create(
        workflow_name="test_workflow_1",
        flow_name="test_flow",
        executed_by=test_user,
    )
    flow.save()

    executor = WorkflowExecutor(flow)
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="start",
        task_name="branch_test",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_a",
        task_name="branched_a_test",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_b",
        task_name="branched_b_test",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="finish_up_a",
        task_name="finish_up_a",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="finish_up_b",
        task_name="finish_up_b",
    ).first()

    assert False


def test_only_group_member_can_execute():
    pass
    # try:
    #     executor.run_flow(user=test_user)
    # except WorkflowNotAuthError as e:
    #     raise PermissionDenied(f"{e}")
