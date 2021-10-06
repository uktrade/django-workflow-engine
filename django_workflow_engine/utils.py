"""django_workflow_engine utils."""
import importlib

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
    for workflow_path in workflows:
        workflow_class = load_workflow(workflow_path)
        display_name = workflow_class.name.title().replace("_", " ")
        choices.append((workflow_class.name, display_name))
    return choices


def lookup_workflow(workflows, name):
    """Look up workflow class.

    Given the configured workflows and a workflow name, returns the associated
    workflow class.

    :param (list) workflows: Configured workflows.
    :param (str) name: Workflow name.
    :returns (class): The requested workflow class.
    :raises (WorkflowImproperlyConfigured): If workflow not found.
    """
    for workflow_path in workflows:
        workflow_class = load_workflow(workflow_path)
        if workflow_class.name == name:
            return workflow_class
    raise WorkflowImproperlyConfigured(f"Cannot find workflow: {name}")


def load_workflow(workflow_path):
    """Load a workflow class.

    Given a workflow path, extrapolates the containing package/modules, imports
    it and loads specified class.

    :param (str) workflow_path: Module path of the work flow including
        class e.g: 'workflows.onboard_contractor.OnboardContractor'
    :returns (class): The workflow class.
    """
    try:
        module_path, cls = workflow_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, cls)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        raise WorkflowImproperlyConfigured(
            f"Failed to load workflow from '{workflow_path}': {e}"
        )
