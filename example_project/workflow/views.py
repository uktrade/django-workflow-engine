from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ValidationError

from .forms import SelectUserForm


User = get_user_model()


def home(request):
    context = {
        "title": "Home",
        "select_user_form": SelectUserForm(initial={"user": request.user.pk})
    }

    return render(request, "workflow/home.html", context=context)


def select_user(request):
    form = SelectUserForm(request.POST)

    if not form.is_valid():
        raise ValidationError("Invalid change user form")

    if form.cleaned_data["user"]:
        new_user = User.objects.get(pk=form.cleaned_data["user"])

        login(request, new_user)
    else:
        logout(request)

    return redirect(reverse("workflow:home"))
