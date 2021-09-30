import uuid

from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.db import models

from django_workflow_engine.exceptions import WorkflowImproperlyConfigured

if not settings.DJANGO_WORKFLOWS:
    raise WorkflowImproperlyConfigured("Add DJANGO_WORKFLOWS to your settings")


class Flow(models.Model):
    WORKFLOWS = [
        (flow, flow.title().replace("_", " "))
        for flow in settings.DJANGO_WORKFLOWS
    ]

    workflow_name = models.CharField(
        "Select workflow", choices=WORKFLOWS, max_length=255
    )
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
    finished = models.DateTimeField(null=True, blank=True)
    flow_info = models.JSONField(default=dict)

    @property
    def is_complete(self):
        return bool(self.finished)

    @property
    def workflow(self):
        return settings.DJANGO_WORKFLOWS[self.workflow_name]

    @property
    def current_task_record(self):
        return self.tasks.filter(finished_at__isnull=True).first()

    # TODO: rename
    @property
    def nice_name(self):
        if self.is_complete:
            return "Completed"
        elif self.started:
            return "In-progress"
        else:
            return "Not started"

    @property
    def on_manual_step(self):
        if not self.current_task_record:
            return False

        current_step = self.workflow.get_step(self.current_task_record.step_id)

        if not current_step:
            return False

        return not self.workflow.get_step(self.current_task_record.step_id).task.auto

    @property
    def continue_url(self):
        return reverse("flow-continue", args=[self.pk])


class TaskRecord(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    executed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name="tasks")
    step_id = models.CharField(max_length=100)
    task_name = models.CharField(max_length=100)
    target = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    task_info = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.step_id} {self.task_name}"


class TaskLog(models.Model):
    logged_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    task_record = models.ForeignKey(
        TaskRecord,
        related_name="log",
        on_delete=models.CASCADE,
    )
