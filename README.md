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
    "django_workflow_engine",
]
```

Add the built-in `django-workflow` view urls to your project's `urls.py`:

```python
urlpatterns = [
    ...
    path('flow/', include('django_workflow_engine.urls')),
]
```

## Building your first workflow

Create a `workflow.py` in your project and add your uniquely named workflows.

```python
from django_workflow_engine import Step, Workflow

Onboard_Contractor = Workflow(
    name="onboard_contractor",
    steps=[
        Step(...),
        Step(...),
        Step(...),
    ],
)

Onboard_Perm = Workflow(
    name="onboard_perm",
    steps=[
        ...
    ],
)
```

Add you workflows to your Django settings as follows:

```python
DJANGO_WORKFLOWS = {
    "onboard_contractor": Onboard_Contractor,
    "onboard_perm": Onboard_Perm,
}
```

Finally, run the `django_workflow` migrations:

```bash
$ ./manage.py migrate
```

Finally, inform the workflow engine of the site domain
> (DC: don't like - use Django Sites?)
```python
DJANGO_WORKFLOWS_SITE = f"https://{ALLOWED_HOSTS[0]}"
```

## Dependencies

## Settings

## Running tests
