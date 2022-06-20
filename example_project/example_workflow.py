from django_workflow_engine import Step, Workflow

from leavers.workflow.tasks import BasicTask, EmailIds  # noqa F401

"""
Leavers Workflow

This can be triggered in 2 places:
- By the Leaver when they notify the Service that they are leaving
- By the Leaver Reporter when they notify the Service that there is a Leaver
"""

LeaversWorkflow = Workflow(
    name="leaving",
    steps=[
        Step(
            step_id="setup_leaving",
            task_name="basic_task",
            start=True,
            targets=[
                "check_uksbs_line_manager",
            ],
        ),
        Step(
            step_id="check_uksbs_line_manager",
            task_name="check_uksbs_line_manager",
            targets=[
                "send_line_manager_correction_reminder",
                "notify_line_manager",
            ],
        ),

        # End
        Step(
            step_id="are_all_tasks_complete",
            task_name="leaver_complete",
            targets=[],
        ),
    ],
)
