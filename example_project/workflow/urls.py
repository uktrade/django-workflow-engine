from django.urls import path

from .views import home, select_user


app_name = "workflow"

urlpatterns = [
    path("", home, name="home"),
    path("select-user/", select_user, name="select-user"),
]
