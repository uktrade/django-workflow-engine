"""django_workflow_engine package interface.

The django_workflow_engine package user utilises these artefacts to build their own
custom workflow e.g:

# I want to build my workflow
from django_workflow_engine import Step, Workflow

# I want to catch workflow errors
from django_workflow_engine import WorkflowError, WorkflowNotAuthError

# I want to derive from base Task
from django_workflow_engine.tasks import Task

# I want to use some built-in tasks
from django_workflow_engine.tasks import SendEmail, EmailFormTask, TaskError
"""
# Workflow definition
from typing import Literal

from .dataclass import Step, Workflow

# Workflow execution
from .exceptions import WorkflowError, WorkflowNotAuthError

# Workflow url generation
from .generate_urls import workflow_urls

# Framework built-ins
from .tasks import EmailFormTask, SendEmail, Task, TaskError

COMPLETE: Literal["complete"] = "complete"
