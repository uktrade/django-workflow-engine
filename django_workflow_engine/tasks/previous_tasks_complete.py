from typing import List

from django_workflow_engine.dataclass import Step
from django_workflow_engine.models import Flow, TaskRecord
from django_workflow_engine.tasks.task import Task


class PreviousTasksCompleteTask(Task):
    task_name = "previous_tasks_complete"
    auto = True

    def execute(self, task_info):
        task_record: TaskRecord = self.task_record
        flow: Flow = self.flow

        leaver_complete_step: Step = flow.workflow.get_step(task_record.step_id)

        # Get all steps that point to the current step.
        previous_steps: List[Step] = [
            step
            for step in flow.workflow.steps
            if step.targets != "complete"
            and leaver_complete_step.step_id in step.targets
        ]

        all_previous_steps_complete: bool = True

        for previous_step in previous_steps:
            previous_step_task_completed: bool = flow.tasks.filter(
                step_id=previous_step.step_id,
                done=True,
            ).exists()

            if not previous_step_task_completed:
                all_previous_steps_complete = False
                break

        return [], all_previous_steps_complete
