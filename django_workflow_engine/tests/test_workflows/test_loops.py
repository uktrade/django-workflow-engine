import pytest
from django_workflow_engine.dataclass import Workflow
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import (
    complex_loops_workflow,
    linear_workflow,
    reminder_workflow,
    split_and_join_workflow,
    split_workflow,
)


@pytest.mark.django_db
def test_linear_workflow(settings):
    """
    All steps in a linear workflow should return that they are NOT in a loop.
    """
    flow, executor, test_user = set_up_flow(
        settings,
        linear_workflow,
    )
    workflow: Workflow = flow.workflow
    loops = workflow.get_loops()
    assert len(loops) == 0
    for step in workflow.steps:
        assert workflow.step_last_in_loop(step.step_id) == False


@pytest.mark.django_db
def test_split_workflow(settings):
    """
    All steps in the split workflow should return that they are NOT in a loop.
    """
    flow, executor, test_user = set_up_flow(
        settings,
        split_workflow,
    )
    workflow: Workflow = flow.workflow
    loops = workflow.get_loops()
    assert len(loops) == 0
    for step in workflow.steps:
        assert workflow.step_last_in_loop(step.step_id) == False


@pytest.mark.django_db
def test_split_and_join_workflow(settings):
    """
    All steps in the split and join workflow should return that they are NOT in a loop.
    """
    flow, executor, test_user = set_up_flow(
        settings,
        split_and_join_workflow,
    )
    workflow: Workflow = flow.workflow
    loops = workflow.get_loops()
    assert len(loops) == 0
    for step in workflow.steps:
        assert workflow.step_last_in_loop(step.step_id) == False


@pytest.mark.django_db
def test_reminder_workflow(settings):
    """
    Reminder workflow contains a loop, so some of the steps should return
    that they are in a loop.
    """
    flow, executor, test_user = set_up_flow(
        settings,
        reminder_workflow,
    )
    workflow: Workflow = flow.workflow
    loops = workflow.get_loops()
    assert len(loops) == 1
    assert loops == [["was_user_created", "remind_creator"]]
    assert workflow.step_last_in_loop("start_reminder") == False
    assert workflow.step_last_in_loop("was_user_created") == False
    assert workflow.step_last_in_loop("remind_creator") == True


@pytest.mark.django_db
def test_complex_loops_workflow(settings):
    """
    The complex loops workflow contains many loops, so some of the steps should return
    that they are in a loop.
    """
    flow, executor, test_user = set_up_flow(
        settings,
        complex_loops_workflow,
    )
    workflow: Workflow = flow.workflow
    loops = workflow.get_loops()
    assert len(loops) == 2
    assert loops == [
        ["task_a_was_user_created", "task_a_remind_creator"],
        ["task_b_was_user_created", "task_b_remind_creator", "task_c"],
    ]
    assert workflow.step_last_in_loop("start") == False
    assert workflow.step_last_in_loop("task_a") == False
    assert workflow.step_last_in_loop("task_a_was_user_created") == False
    assert workflow.step_last_in_loop("task_a_remind_creator") == True
    assert workflow.step_last_in_loop("task_a_notify_creator") == False
    assert workflow.step_last_in_loop("task_b") == False
    assert workflow.step_last_in_loop("task_b_was_user_created") == False
    assert workflow.step_last_in_loop("task_b_remind_creator") == False
    assert workflow.step_last_in_loop("task_c") == True
    assert workflow.step_last_in_loop("task_b_notify_creator") == False
    assert workflow.step_last_in_loop("end") == False
