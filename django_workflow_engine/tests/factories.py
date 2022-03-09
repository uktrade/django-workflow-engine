from typing import TYPE_CHECKING, Optional

from django.contrib.auth import get_user_model
from django_workflow_engine import COMPLETE
from django_workflow_engine.dataclass import Step, Workflow
from django_workflow_engine.tasks.task import Task
from django_workflow_engine.tests.tasks import BasicTask
from factory import Factory, Sequence, post_generation
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
