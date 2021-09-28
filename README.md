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

Add the built-in `django-workflow` view urls to your project's `urls.py`:

```python
urlpatterns = [
    ...
    path('dwflow/', include('django_workflow.urls')),
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

## Dependencies

## Settings

## Running tests
