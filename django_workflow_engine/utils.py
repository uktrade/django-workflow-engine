"""django_workflow_engine utils."""
import importlib

from .exceptions import WorkflowImproperlyConfigured


def build_workflow_choices(workflows):
    """Build workflow choices.

    Builds a choices list by iterating over the workflows dict
    provided.

    :param (dict) workflows: Map of workflow name to full module path of
        workflow including class e.g:
        {'onboard_contractor: 'workflows.onboard_contractor.OnboardContractor, ...}
    """
    choices = []
    for workflow_name in workflows:
        workflow_path = workflows[workflow_name]
        workflow_class = lookup_workflow(workflow_path)
        choices.append((workflow_class, workflow_name))
    return choices


def lookup_workflow(workflow_path):
    """Look up a workflow class.

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
