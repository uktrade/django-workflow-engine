from django.utils import timezone

from .exceptions import WorkflowError, WorkflowNotAuthError
from django_workflow_engine.models import TaskRecord


class WorkflowExecutor:
    def __init__(self, flow):
        self.flow = flow

    def run_flow(self, user, task_info=None, task_uuid=None):
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
        if self.flow.started and not task_uuid:
            raise WorkflowError("Flow already started")

        current_step = self.get_current_step(self.flow, task_uuid)
        while current_step:
            task_record, created = TaskRecord.objects.get_or_create(
                flow=self.flow,
                task_name=current_step.task_name,
                step_id=current_step.step_id,
                executed_by=None,
                finished_at=None,
                defaults={"task_info": current_step.task_info or {}},
            )

            task = current_step.task(user, task_record, self.flow)

            task.setup(task_info)

            # the next task has a manual step
            if not task.auto and created:
                return task_record

            self.check_authorised(user, current_step)  # Raises if user not authorised for step
            target, task_output = task.execute(task_info)

            # TODO: check target against step target

            task_record.finished_at = timezone.now()
            task_record.save()
            self.flow.save()

            current_step = next(
                (
                    step
                    for step in self.flow.workflow.steps
                    if step.step_id == (target or current_step.target)
                ),
                None,
            )

            task_info = task_output

        self.flow.finished = timezone.now()
        self.flow.save()

        return task_record

    @staticmethod
    def get_current_step(flow, task_uuid=None):
        """Get the current step.

        If a task uuid is provided we retrieve the related task record/step
        otherwise use the workflow's designated first step.

        :param (Flow) flow: the workflow.
        :param (str) task_uuid: UUID of the current task or None.
        :returns (Step): A workflow step.
        """
        if task_uuid:
            current_step = flow.workflow.get_step(
                TaskRecord.objects.get(uuid=task_uuid).step_id
            )
        else:
            current_step = flow.workflow.first_step
            flow.started = timezone.now()
            flow.save()
        return current_step

    @staticmethod
    def check_authorised(user, step):
        """Check user is authorised.

        Check that a user is authorised to execute a workflow step.

        :param (User) user: Workflow user.
        :param (Step) step: Flow step.
        :raises (WorkflowNotAuthError): If user is not authorised.
        """
        user_groups = set(g.name for g in user.groups.all())
        required_groups = set(step.groups)
        if user_groups.intersection(required_groups):
            return
        msg = (
            f"User '{user}' is not authorised to execute the "
            f"step: {step.task_name}"
        )
        raise WorkflowNotAuthError(msg)
