import logging

from django.utils import timezone

from .exceptions import WorkflowError, WorkflowNotAuthError
from django_workflow_engine.models import TaskRecord, Target
from django_workflow_engine import COMPLETE


logger = logging.getLogger(__name__)


class WorkflowExecutor:
    def __init__(self, flow):
        self.flow = flow

    def run_flow(self, user, task_info=None, task_uuids=None):
        """Run the workflow.

        We identify the current step and execute workflow steps until a manual
        step is encountered (e.g. complete a form) or the workflow is exhausted.

        :param (User) user: User requesting to run a flow step.
        :param (dict) task_info: Additional task info.
        :param (str) task_uuid: Task record UUID.
        :returns (TaskRecord): New or updated task record.
        """
        if task_info is None:
            task_info = {}

        # TODO: might be a race condition
        if self.flow.started and not task_uuids:
            raise WorkflowError("Flow already started")

        current_steps = self.get_current_step(self.flow, task_uuids)
        task_record, break_flow = self.execute_steps(
            user,
            current_steps,
            task_info,
            False,
            True,
        )

        if not break_flow:
            self.flow.finished = timezone.now()
            self.flow.save()

        return task_record

    def execute_steps(
        self,
        user,
        current_steps,
        task_info,
        break_flow,
        first_run,
    ):
        task_record = None

        for current_step in current_steps:
            task_record, created = TaskRecord.objects.get_or_create(
                flow=self.flow,
                task_name=current_step.task_name,
                step_id=current_step.step_id,
                executed_by=None,
                finished_at=None,
                defaults={"task_info": current_step.task_info or {}},
                broke_flow=current_step.break_flow,
            )

            task = current_step.task(user, task_record, self.flow)
            task.setup(task_info)

            # the next task has a manual step
            if not task.auto and created:
                return task_record

            self.check_authorised(user, current_step)  # Raises if user not authorised for step

            targets, task_output = task.execute(task_info)

            # Default tasks will have None target
            # So we want step targets to be used
            if not targets:
                targets = current_step.targets

            task_record.finished_at = timezone.now()
            task_record.save()
            self.flow.save()

            current_steps = []

            if targets and targets != COMPLETE:
                for target in targets:
                    Target.objects.get_or_create(
                        task_record=task_record,
                        target_string=target
                    )

                for step in self.flow.workflow.steps:
                    if current_step.targets:
                        if step.step_id in targets or step.step_id in current_step.targets:
                            current_steps.append(step)

            task_info = task_output

            if current_step.break_flow and not first_run:
                break_flow = True
            else:
                first_run = False

                if len(current_steps) > 0:
                    task_record, break_flow = self.execute_steps(user, current_steps, task_info, break_flow, first_run)

        return task_record, break_flow

    @staticmethod
    def get_current_step(flow, task_uuids=None):
        """Get the current step.

        If a task uuid is provided we retrieve the related task record/step
        otherwise use the workflow's designated first step.

        :param (Flow) flow: the workflow.
        :param (list) task_uuids: UUID of the current task or None.
        :returns (Step): A workflow step.
        """
        current_steps = []
        if task_uuids:
            for task_uuid in task_uuids:
                # TODO - error handling
                task = TaskRecord.objects.get(uuid=task_uuid)

                if task.broke_flow:
                    task = TaskRecord.objects.get(uuid=task_uuid)

                    targets = Target.objects.filter(
                        task_record=task,
                    ).all()

                    for target in targets:
                        next_task = TaskRecord.objects.filter(
                            step_id=target.target_string,
                        ).first()

                        if next_task:
                            task = next_task

                current_steps.append(flow.workflow.get_step(
                        task.step_id
                    )
                )
        else:
            current_steps.append(flow.workflow.first_step)
            flow.started = timezone.now()
            flow.save()

        return current_steps

    @staticmethod
    def check_authorised(user, step):
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
        msg = (
            f"User '{user}' is not authorised to execute the "
            f"step: {step.task_name}"
        )
        raise WorkflowNotAuthError(msg)
