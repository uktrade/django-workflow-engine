import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.manager import BaseManager
from django.urls import reverse

from django_workflow_engine.dataclass import Workflow
from django_workflow_engine.exceptions import WorkflowImproperlyConfigured
from django_workflow_engine.utils import lookup_workflow

if not hasattr(settings, "DJANGO_WORKFLOWS"):
    raise WorkflowImproperlyConfigured("Add DJANGO_WORKFLOWS to your settings")


class Flow(models.Model):
    workflow_name = models.CharField("Select workflow", max_length=255)
    flow_name = models.CharField(
        "Select activity",
        max_length=255,
        help_text="e.g. Hire a Python Developer",
    )
    executed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    started = models.DateTimeField(null=True)
    running = models.BooleanField(default=False)
    finished = models.DateTimeField(null=True, blank=True)
    flow_info = models.JSONField(default=dict)

    tasks: BaseManager["TaskStatus"]

    @property
    def is_complete(self):
        return bool(self.finished)

    @property
    def workflow(self) -> Workflow:
        return lookup_workflow(self.workflow_name)

    @property
    def current_task_status(self):
        return self.tasks.filter(done=False, executed_at__isnull=True).first()

    @property
    def status(self):
        if self.is_complete:
            return "Completed"
        elif self.started:
            return "In-progress"
        else:
            return "Not started"

    @property
    def on_manual_step(self):
        if not self.current_task_status:
            return False

        current_step = self.workflow.get_step(self.current_task_status.step_id)

        if not current_step:
            return False

        return not self.workflow.get_step(self.current_task_status.step_id).task.auto

    @property
    def continue_url(self):
        return reverse("flow-continue", args=[self.pk])


class TaskStatus(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True)
    executed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
    )
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name="tasks")
    step_id = models.CharField(max_length=100)
    task_name = models.CharField(max_length=100)
    task_info = models.JSONField(default=dict)
    done = models.BooleanField(default=False)

    targets: BaseManager["Target"]
    log: BaseManager["TaskLog"]

    def __str__(self):
        return f"{self.step_id} {self.task_name}"


class Target(models.Model):
    target_string = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    task_status = models.ForeignKey(
        TaskStatus,
        on_delete=models.CASCADE,
        related_name="targets",
    )

    class Meta:
        unique_together = ("target_string", "task_status")


class TaskLog(models.Model):
    logged_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    task_status = models.ForeignKey(
        TaskStatus,
        related_name="log",
        on_delete=models.CASCADE,
    )


"""
Old models kept for reference.
"""


class TaskRecordExecution(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True)
    executed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="task_executions",
    )
    flow = models.ForeignKey(
        Flow, on_delete=models.CASCADE, related_name="task_executions"
    )
    step_id = models.CharField(max_length=100)
    task_name = models.CharField(max_length=100)
    task_info = models.JSONField(default=dict)
    done = models.BooleanField(default=False)

    targets: BaseManager["TaskRecordExecutionTarget"]
    log: BaseManager["TaskRecordExecutionTaskLog"]

    def __str__(self):
        return f"{self.step_id} {self.task_name}"


class TaskRecordExecutionTarget(models.Model):
    target_string = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    task_record = models.ForeignKey(
        "TaskRecordExecution",
        on_delete=models.CASCADE,
        related_name="targets",
    )


class TaskRecordExecutionTaskLog(models.Model):
    logged_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    task_record = models.ForeignKey(
        "TaskRecordExecution",
        related_name="log",
        on_delete=models.CASCADE,
    )
