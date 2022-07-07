"""django_workflow_engine package urls.

Provides easy defaults or option to override some or all of the built in views,
for example in the client project's urls.py:

    from django_workflow_engine import workflow_urls
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
from django.urls import include, path


def workflow_urls(
    list_view=None,
    create_view=None,
    view=None,
    continue_view=None,
    diagram_view=None,
    delete_view=None,
):
    """Generate workflow urls.

    Generate route config while providing the option for the the package user
    to specify their own view class overrides.

    :param (View) list_view: Alternative to FlowListView.
    :param (View) create_view: Alternative to FlowCreateView.
    :param (View) view: Alternative to FlowView.
    :param (View) continue_view: Alternative to FlowContinueView.
    :param (View) diagram_view: Alternative to FlowDiagramView.
    :param (View) delete_view: Alternative to FlowDeleteView.
    :returns (tuple): result django.urls.include invocation.
    """
    import django_workflow_engine.views as workflow_views  # Avoid circular import

    list_view = list_view if list_view else workflow_views.FlowListView
    view = view if view else workflow_views.FlowView
    create_view = create_view if create_view else workflow_views.FlowCreateView
    continue_view = continue_view if continue_view else workflow_views.FlowContinueView
    diagram_view = diagram_view if diagram_view else workflow_views.FlowDiagramView
    delete_view = delete_view or workflow_views.FlowDeleteView

    return include(
        [
            path("", list_view.as_view(), name="flow-list"),
            path("new", create_view.as_view(), name="flow-create"),
            path("<int:pk>/", view.as_view(), name="flow"),
            path("<int:pk>/continue", continue_view.as_view(), name="flow-continue"),
            path("<int:pk>/diagram", diagram_view.as_view(), name="flow-diagram"),
            path("<int:pk>/delete", delete_view.as_view(), name="flow-delete"),
        ]
    )
