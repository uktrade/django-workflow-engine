"""django_workflow_engine package urls."""

from django.urls import path

import django_workflow_engine.views as workflow_views


urlpatterns = [
    path("", workflow_views.FlowListView.as_view(), name="flow-list"),
    path("new", workflow_views.FlowCreateView.as_view(), name="flow-create"),
    path("delete/<int:pk>/", workflow_views.FlowDeleteView.as_view(), name="flow-delete"),
    path("<int:pk>/", workflow_views.FlowView.as_view(), name="flow"),
    path(
        "<int:pk>/continue",
        workflow_views.FlowContinueView.as_view(),
        name="flow-continue",
    ),
    path(
        "<int:pk>/diagram",
        workflow_views.FlowDiagramView.as_view(),
        name="flow-diagram",
    ),
]
