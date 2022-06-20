"""django_workflow_engine package framework dataclasses.

Dataclasses that are used to define a custom workflow and its steps.
"""
from dataclasses import dataclass, field
from typing import Optional, Any

from .tasks import Task


@dataclass
class Step:
    step_id: str
    task_name: str
    targets: Optional[list[str]]
    start: Optional[bool] = None
    task_info: Optional[dict] = None
    description: Optional[str] = None
    groups: list[str] = field(default_factory=list)
    no_log: Optional[bool] = False
    break_flow: Optional[bool] = False
    pool: Optional[str] = None
    lane: Optional[str] = None
    description: Optional[str] = None
    decision_text: Optional[str] = None

    @property
    def task(self):
        return Task.tasks[self.task_name]


@dataclass
class Workflow:
    name: str
    steps: list[Step]

    def get_step(self, step_id):
        return next((step for step in self.steps if step.step_id == step_id), None)

    @property
    def first_step(self):
        return next(step for step in self.steps if step.start)
