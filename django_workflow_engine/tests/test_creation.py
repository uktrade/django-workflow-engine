import pytest

from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import linear_workflow


@pytest.mark.django_db
def test_workflow_creation(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        linear_workflow,
    )
    executor.run_flow(user=test_user)


def test_only_group_member_can_execute():
    # TODO
    pass
