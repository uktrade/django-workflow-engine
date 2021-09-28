"""django_workflow package interface.

The django_workflow package user utilises these artefacts to build their own
custom workflow e.g:

# I want to build my workflow
from django_workflow import Step, Workflow

# I want to derive from base Task
from django_workflow.tasks import Task

# I want to use some built-in tasks
from django_workflow.tasks import SendEmail, EmailFormTask, TaskError
"""
from .framework import Step
from .framework import Workflow
from .framework import tasks
