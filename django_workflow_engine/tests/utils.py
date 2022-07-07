from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow
from django_workflow_engine.tests.factories import UserFactory


def set_up_flow(settings, workflow):
    test_user = UserFactory()

    settings.DJANGO_WORKFLOWS = {
        "test_workflow": workflow,
    }

    flow = Flow.objects.create(
        workflow_name="test_workflow",
        flow_name="test_flow",
        executed_by=test_user,
    )
    flow.save()

    executor = WorkflowExecutor(flow)

    return flow, executor, test_user
