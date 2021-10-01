"""django_workflow_engine package urls.

Provides easy defaults or option to override some or all of the build in views,
for example in the client project's urls.py:

    from django-workflow-engine import workflow_urls
    ...
    urlpatterns = [
        # django-workflow-engine OTB view classes
        path("workflow/", workflow_urls()),
        ...
    ]

Alternatively provide own view classes for flow list and flow view:

    urlpatterns = [
        path(
            "workflow/",
            workflow_urls(
                list_view=MyFlowListView,
                view=MyFlowView,
            ),
        ),
    ]
"""
from django.urls import path, include


def workflow_urls(**kwargs):
    """Generate workflow urls.

    Generate route config while providing the option for the the package user
    to specify their own view class overrides.

    :param (dict) kwargs: classes to override.
    :returns (tuple): result django.urls.include invocation.
    """
    import django_workflow_engine.views as workflow_views  # Avoid circular deps
    list_view = kwargs.get("list_view", workflow_views.FlowListView)
    view = kwargs.get("view", workflow_views.FlowView)
    create_view = kwargs.get("create_view", workflow_views.FlowCreateView)
    continue_view = kwargs.get("continue_view", workflow_views.FlowContinueView)
    diagram_view = kwargs.get("diagram_view", workflow_views.FlowDiagramView)
    return include(
        [
            path("", list_view.as_view(), name="flow-list"),
            path("<int:pk>/", view.as_view(), name="flow"),
            path("new", create_view.as_view(), name="flow-create"),
            path("<int:pk>/continue", continue_view.as_view(), name="flow-continue"),
            path("<int:pk>/diagram", diagram_view.as_view(), name="flow-diagram"),
        ]
    )
