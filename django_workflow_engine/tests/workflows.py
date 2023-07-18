from django_workflow_engine import COMPLETE
from django_workflow_engine.dataclass import Step, Workflow
from django_workflow_engine.tasks.previous_tasks_complete import (
    PreviousTasksCompleteTask,
)
from django_workflow_engine.tests.tasks import BasicTask, InvalidTargetTask, PauseTask

"""
Test workflow definitions

Tests for these can be found in "/django_workflow_engine/tests/test_workflows/"
Where the file name is "test_{workflow_name}.py"
Example: `linear_workflow` can be found at "test_linear_workflow.py"
"""

linear_workflow = Workflow(
    name="linear_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["task_b"],
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

split_workflow = Workflow(
    name="split_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a", "task_b"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["finish_task_a"],
        ),
        Step(
            step_id="finish_task_a",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=["finish_task_b"],
        ),
        Step(
            step_id="finish_task_b",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)


split_and_join_workflow = Workflow(
    name="split_and_join_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a", "task_b"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_c",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

previous_tasks_complete_workflow = Workflow(
    name="previous_tasks_complete",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a", "task_b"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_c",
            task_name=PreviousTasksCompleteTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

previous_tasks_complete_failure_workflow = Workflow(
    name="previous_tasks_complete",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a", "task_b"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_b",
            task_name=PauseTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_c",
            task_name=PreviousTasksCompleteTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

pause_task_workflow = Workflow(
    name="pause_task_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["pause"],
        ),
        Step(
            step_id="pause",
            task_name=PauseTask.task_name,
            targets=["end"],
        ),
        Step(
            step_id="end",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)
self_ref_pause_task_workflow = Workflow(
    name="self_ref_pause_task_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["pause"],
        ),
        Step(
            step_id="pause",
            task_name=PauseTask.task_name,
            targets=["end"],
        ),
        Step(
            step_id="end",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

reminder_workflow = Workflow(
    name="reminder_workflow",
    steps=[
        Step(
            step_id="start_reminder",
            task_name=BasicTask.task_name,
            start=True,
            targets=["was_user_created"],
        ),
        Step(
            step_id="was_user_created",
            task_name="was_user_created",
            targets=["remind_creator", "notify_creator"],
        ),
        Step(
            step_id="remind_creator",
            task_name=BasicTask.task_name,
            targets=["was_user_created"],
        ),
        Step(
            step_id="notify_creator",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)

complex_loops_workflow = Workflow(
    name="reminder_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a", "task_b"],
        ),
        Step(
            step_id="task_a",
            task_name=BasicTask.task_name,
            targets=["task_a_was_user_created"],
        ),
        Step(
            step_id="task_a_was_user_created",
            task_name="was_user_created_task_a",
            targets=["task_a_remind_creator", "task_a_notify_creator"],
        ),
        Step(
            step_id="task_a_remind_creator",
            task_name=BasicTask.task_name,
            targets=["task_a_was_user_created"],
        ),
        Step(
            step_id="task_a_notify_creator",
            task_name=BasicTask.task_name,
            targets=["end"],
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=["task_b_was_user_created"],
        ),
        Step(
            step_id="task_b_was_user_created",
            task_name="was_user_created_task_b",
            targets=["task_b_remind_creator", "task_b_notify_creator"],
        ),
        Step(
            step_id="task_b_remind_creator",
            task_name=BasicTask.task_name,
            targets=["task_c"],
        ),
        Step(
            step_id="task_c",
            task_name=BasicTask.task_name,
            targets=["task_b_was_user_created"],
        ),
        Step(
            step_id="task_b_notify_creator",
            task_name=BasicTask.task_name,
            targets=["end"],
        ),
        Step(
            step_id="end",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)


invalid_task_target_workflow = Workflow(
    name="invalid_task_target_workflow",
    steps=[
        Step(
            step_id="start",
            task_name=BasicTask.task_name,
            start=True,
            targets=["task_a"],
        ),
        Step(
            step_id="task_a",
            task_name=InvalidTargetTask.task_name,
            targets=["task_b"],
        ),
        Step(
            step_id="task_b",
            task_name=BasicTask.task_name,
            targets=COMPLETE,
        ),
    ],
)
