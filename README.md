# django-workflow-engine
`django-workflow` is a lightweight and reusable workflow engine for
Django applications. It enables you to better organise the business logic for
collaborating users.

## Installation

    pip install django-workflow-engine

## Getting started
Add the application to your Django settings `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    "django_workflow_engine",
]
```

Add the built-in `django-workflow-engine` view urls to your project's `urls.
py` as
follows:


```python
from django_workflow_engine import workflow_urls
...
urlpatterns = [
    path("workflow/", workflow_urls()),
    ...
]
```

This will utilise all `django-workflow-engine` built-in view classes. Default views are:
- `list_view=FlowListView` List of workflow instances view.
- `view=FlowView` Workflow instance view.
- `create_view=FlowCreateView` Create workflow view.
- `continue_view=FlowContinueView` Workflow continuation view.
- `diagram_view=FlowDiagramView` Workflow diagram view.

You can override any the built-in view classes with your own, for example to
provide your own view classes for flow list and flow view:

```python
urlpatterns = [
        path("workflow/",
             workflow_urls(
                 list_view=MyFlowListView,
                 view=MyFlowView,
            ),
        ),
    ]
```

## Building your first workflow

Create a `workflows.py` in your project and add your uniquely named workflows.

```python
from django_workflow_engine import Step, Workflow

onboard_contractor = Workflow(
    name="onboard_contractor",
    steps=[
        Step(...),
        Step(...),
        Step(...),
    ],
)

onboard_perm = Workflow(
    name="onboard_perm",
    steps=[
        ...
    ],
)
```

Add you workflows to your Django settings as follows:

```python
DJANGO_WORKFLOWS = {
    "onboard_contractor": "your_app.workflows.onboard_contractor",
    "onboard_perm": "your_app.workflows.onboard_perm",
}
```

Each entry needs to be a valid module path where the final component is the
name of your workflow class.

Finally, run the `django-workflow-engine` migrations:

```bash
$ ./manage.py migrate
```

## Pushing to PyPI

- [PyPI Package](https://pypi.org/project/django-workflow-engine/)
- [Test PyPI Package](https://test.pypi.org/project/django-workflow-engine/)

Running `make build-package` will build the package into the `dist/` directory
Running `make push-pypi-test` will push the built package to Test PyPI
Running `make push-pypi` will push the built package to PyPI

### Setting up poetry for pushing to PyPI

First you will need to add the test pypy repository to your poetry config:

```
poetry config repositories.test-pypi https://test.pypi.org/legacy/
```

Then go to https://test.pypi.org/manage/account/token/ and generate a token.

Then add it to your poetry config:

```
poetry config pypi-token.test-pypi XXXXXXXX
```

Then you also need to go to https://pypi.org/manage/account/token/ to generate a token for the real PyPI.

Then add it to your poetry config:

```
poetry config pypi-token.pypi XXXXXXXX
```

Now the make commands should work as expected.


## Dependencies

## Settings

## Running tests
