"""Urls for django_workflow app container."""
from django.urls import path, include

urlpatterns = [
    path('flow/', include('django_workflow.urls')),
]
