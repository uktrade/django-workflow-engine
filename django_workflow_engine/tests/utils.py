from django.contrib.auth.models import User

from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow


def create_test_user(
    first_name="John",
    last_name="Smith",
    email="john.smith@test.com",
    username="john_smith",
) -> User:
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
    )
    user.set_password("password")
    user.save()

    return user


def set_up_flow(settings, workflow):
    test_user = create_test_user()

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
