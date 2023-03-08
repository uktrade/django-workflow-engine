"""django_workflow_engine utils."""
from typing import Dict, Type, Union, cast

from django.conf import settings
from django.utils.module_loading import import_string

from django_workflow_engine.dataclass import Workflow

from .exceptions import WorkflowImproperlyConfigured


def build_workflow_choices(workflows):
    """Build workflow choices.

    Builds a choices list by iterating over the workflows dict
    provided.

    :param (list) workflows: List of workflows, module path of workflow
        including class e.g: ['workflows.onboard_contractor.OnboardContractor, ...]
    :returns (list[Tuple]): List of tuples (workflow class name, display name)
    """
    choices = []
    for display_name, workflow_path in workflows.items():
        workflow_class = load_workflow(display_name)
        choices.append((workflow_class.name, display_name))
    return choices


def lookup_workflow(workflow_name) -> Workflow:
    """Look up workflow class.

    Given the configured workflows and a workflow name, returns the associated
    workflow class.

    :param (list) workflows: Configured workflows.
    :param (str) name: Workflow name.
    :returns (class): The requested workflow class.
    :raises (WorkflowImproperlyConfigured): If workflow not found.
    """

    for display_name, workflow_path in settings.DJANGO_WORKFLOWS.items():
        if display_name == workflow_name:
            workflow_class = load_workflow(display_name)
            return workflow_class
    raise WorkflowImproperlyConfigured(f"Cannot find workflow: {display_name}")


def load_workflow(workflow_key) -> Workflow:
    """Load a workflow class.

    Given a workflow path, extrapolates the containing package/modules, imports
    it and loads specified class.

    :param (str) workflow_path: Module path of the work flow including
        class e.g: 'workflows.onboard_contractor.OnboardContractor'
    :returns (class): The workflow class.
    """
    workflows = cast(Dict[str, Union[Workflow, str]], settings.DJANGO_WORKFLOWS)
    class_or_str = workflows[workflow_key]

    if type(class_or_str) is Workflow:
        return class_or_str

    assert type(class_or_str) is str

    try:
        return import_string(class_or_str)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        raise WorkflowImproperlyConfigured(
            f"Failed to load workflow from '{class_or_str}': {e}"
        )
