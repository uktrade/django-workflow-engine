from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


def get_user_choices():
    yield None, "-----"

    for user in User.objects.all():
        yield user.pk, user.username


class SelectUserForm(forms.Form):
    user = forms.ChoiceField(choices=get_user_choices, required=False)
