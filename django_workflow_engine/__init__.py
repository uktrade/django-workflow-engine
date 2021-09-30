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
from .dataclass import Step
from .dataclass import Workflow

# Workflow execution
from .exceptions import WorkflowError
from .exceptions import WorkflowNotAuthError

# Framework built-ins
from .tasks import SendEmail
from .tasks import EmailFormTask
from .tasks import Task, TaskError
