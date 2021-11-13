from django.contrib.auth.models import User


def create_test_user() -> User:
    user = User.objects.create(
        first_name="John",
        last_name="Smith",
        email="john.smith@test.com",
        username="john_smith",
    )
    user.set_password("password")
    user.save()

    return user
