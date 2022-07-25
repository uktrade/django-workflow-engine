import logging
from typing import TYPE_CHECKING, List, Tuple, Type

from django.contrib.auth import get_user_model
from django.utils import timezone

from django_workflow_engine import COMPLETE
from django_workflow_engine.exceptions import WorkflowError, WorkflowNotAuthError
from django_workflow_engine.models import Target, TaskRecord

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_workflow_engine.dataclass import Step
    from django_workflow_engine.models import Flow
    from django_workflow_engine.tasks.task import Task
else:
    User = get_user_model()


logger = logging.getLogger(__name__)


class WorkflowExecutor:
    def __init__(self, flow: "Flow"):
        self.flow: "Flow" = flow

    def run_flow(self, user: User) -> None:
        """
        Run the workflow.

        We identify the current step and execute workflow steps until a manual
        step is encountered (e.g. complete a form) or the workflow is exhausted.

        :param (User) user: User requesting to run a flow step.
        """

        if self.flow.running:
            raise WorkflowError("Flow already running")

        # Mark the flow as running (an attempt to prevent concurrent execution of the same Flow)
        self.flow.running = True
        self.flow.save(update_fields=["running"])

        try:
            # Progress the workflow
            self.execute_steps(user=user)
        except Exception as e:
            self.flow.running = False
            self.flow.save(update_fields=["running"])
            raise e

        # If the flow has no remaining steps, then we are done.
        remaining_steps = self.get_current_steps()
        if not remaining_steps:
            self.flow.finished = timezone.now()

        # Mark the flow as not running, so that it can be picked up again.
        self.flow.running = False
        self.flow.save(update_fields=["running", "finished"])

    def execute_steps(self, user: User):
        """
        Execute any steps that have not been complete.

        This function is recursive/self referencing.
        """
        break_flow: bool = False

        # Get all of the steps that need to be executed.
        current_steps = self.get_current_steps()

        # If there is nothing to execute, then we are done.
        if not current_steps:
            return break_flow

        # Execute the steps.
        for current_step in current_steps:
            current_step_break_flow = self.execute_step(user=user, step=current_step)
            # We want to toggle break_flow to True, but not back to False.
            if current_step_break_flow:
                break_flow = True

        # If we have broken the flow, then we are done, any remaining tasks will
        # be picked up next time.
        if break_flow:
            return None

        # Call this function again to execute the next steps.
        self.execute_steps(user=user)

    def execute_step(
        self,
        user: User,
        step: "Step",
    ) -> bool:
        """
        Execute the task for the given step.

        Generate any of the resulting tasks.
        """
        break_flow: bool = False

        task_record, _ = self.get_or_create_task_record(step=step)

        # Get the task for the current step
        step_task: Type["Task"] = step.task
        # Instantiate the Task
        task = step_task(user, task_record, self.flow)
        # Setup the Task.
        task.setup(task_record.task_info)

        # Check if this task is automatic or manual
        if not task.auto:
            return break_flow

        # Raises if user not authorised for step
        self.check_authorised(user, step)

        # Execute the task
        targets, task_done = task.execute(task_record.task_info)

        task_record.done = task_done
        task_record.executed_by = user
        task_record.executed_at = timezone.now()
        task_record.save()

        if targets is None:
            targets = []

        # If the task didn't return targets, we only use step targets if
        # the task is done.
        if not targets:
            if task_done:
                targets = step.targets
            else:
                # If the task is not done, then re-add the step to the targets.
                targets.append(step.step_id)

        # Create objects for the next tasks, generated after the current.
        if targets and targets != COMPLETE:
            for target in targets:
                Target.objects.get_or_create(
                    task_record=task_record, target_string=target
                )
            for workflow_step in self.flow.workflow.steps:
                if workflow_step.step_id in targets:
                    self.get_or_create_task_record(step=workflow_step)

        # Break the flow if this task is the last in a loop or if the task isn't done or if this step is in the target list.
        if (
            self.flow.workflow.step_last_in_loop(step.step_id)
            or not task_done
            or step.step_id in targets
        ):
            break_flow = True

        return break_flow

    def get_or_create_task_record(self, step: "Step") -> Tuple[TaskRecord, bool]:
        """
        Get or create a TaskRecord for a given Step.
        """

        task_record, created = TaskRecord.objects.get_or_create(
            flow=self.flow,
            task_name=step.task_name,
            step_id=step.step_id,
            executed_by=None,
            executed_at=None,
            defaults={"task_info": step.task_info or {}},
        )
        return task_record, created

    def get_current_steps(self) -> List["Step"]:
        """
        Get the current steps.
        """

        current_steps: List["Step"] = []

        # Get all TaskRecords that haven't been executed yet.
        for task in self.flow.tasks.filter(executed_at__isnull=True):
            current_steps.append(self.flow.workflow.get_step(task.step_id))

        if not current_steps and not self.flow.started:
            # If there are no steps and the flow has never started, then start the flow from the first step.
            current_steps.append(self.flow.workflow.first_step)
            self.flow.started = timezone.now()
            self.flow.save(update_fields=["started"])

        return current_steps

    @staticmethod
    def check_authorised(user: User, step: "Step"):
        """Check if a user is authorised to execute a workflow step.

        If no groups are defined on the step, the check will pass and permission will be
        granted.

        :param (User) user: Workflow user.
        :param (Step) step: Flow step.
        :raises (WorkflowNotAuthError): If user is not authorised.
        """
        if not step.groups:
            return

        if user.groups.filter(name__in=step.groups).exists():
            return
        msg = f"User '{user}' is not authorised to execute the step: {step.task_name}"
        raise WorkflowNotAuthError(msg)
