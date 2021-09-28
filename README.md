# django-workflow
`django-workflow` is a lightweight and reusable workflow engine for 
Django applications. It enables you to better organise the business logic for 
collaborating users.

## Installation

    pip install django-workflow

## Getting started
Add the application to your Django settings `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    "django_workflow",
]
```

## Building your first workflow

```python
from django_workflow import Step, Workflow

MyWorkflow = Workflow(
    name="my_workflow",
    steps=[
        Step(...),
        Step(...),
        Step(...),        
    ],
)
```
from workflow.dataclasses import Step, Workflow


ApprovalWorkflow = Workflow(
name="approval_workflow",
steps=[
Step(


## Dependencies

## Settings

## Running tests
