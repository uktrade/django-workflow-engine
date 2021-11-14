import pytest

from django.conf import settings

from django_workflow_engine import Workflow, Step, Task
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow, TaskRecord

from django_workflow_engine.tests.utils import create_test_user


class BasicTask(Task):
    task_name = "basic_task"
    auto = True

    def execute(self, task_info):
        return None, {}


@pytest.mark.django_db
def test_workflow_creation(settings):
    test_user = create_test_user()

    test_workflow = Workflow(
        name="test_workflow_1",
        steps=[
            Step(
                step_id="test_task",
                task_name="basic_task",
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


class FinishMeetUpTaskA(Task):
    task_name = "finish_meet_up_a"
    auto = True

    def execute(self, task_info):
        return ["meet_up", ], {}


class FinishMeetUpTaskB(Task):
    task_name = "finish_meet_up_b"
    auto = True

    def execute(self, task_info):
        return ["meet_up", ], {}


class MeetUp(Task):
    task_name = "meet_up"
    auto = True

    def execute(self, task_info):
        return None, {}


@pytest.mark.django_db
def test_parallel_path_no_join_workflow(settings):
    test_user = create_test_user()

    test_workflow = Workflow(
        name="test_workflow_1",
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

    assert TaskRecord.objects.count() == 5

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="start",
        task_name="start",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_a",
        task_name="task_a",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_b",
        task_name="task_b",
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


@pytest.mark.django_db
def test_parallel_path_join_up_workflow(settings):
    test_user = create_test_user()

    test_workflow = Workflow(
        name="test_workflow_1",
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
                target=["finish_meet_up_a"],
            ),
            Step(
                step_id="task_b",
                task_name="task_b",
                target=["finish_meet_up_b"],
            ),
            Step(
                step_id="finish_meet_up_a",
                task_name="finish_meet_up_a",
                target=["meet_up", ],
            ),
            Step(
                step_id="finish_meet_up_b",
                task_name="finish_meet_up_b",
                target=["meet_up", ],
            ),
            Step(
                step_id="meet_up",
                task_name="meet_up",
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

    assert TaskRecord.objects.count() == 7

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="start",
        task_name="start",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_a",
        task_name="task_a",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="task_b",
        task_name="task_b",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="finish_meet_up_a",
        task_name="finish_meet_up_a",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="finish_meet_up_b",
        task_name="finish_meet_up_b",
    ).first()

    assert TaskRecord.objects.filter(
        flow=flow,
        step_id="meet_up",
        task_name="meet_up",
    ).count() == 2


def test_only_group_member_can_execute():
    pass
    # try:
    #     executor.run_flow(user=test_user)
    # except WorkflowNotAuthError as e:
    #     raise PermissionDenied(f"{e}")
