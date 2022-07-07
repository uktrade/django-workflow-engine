from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from factory import Sequence
from factory.django import DjangoModelFactory

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user{n}")
    email = Sequence(lambda n: f"email{n}@example.com")
    first_name = Sequence(lambda n: f"FirstName{n}")
    last_name = Sequence(lambda n: f"LastName{n}")
