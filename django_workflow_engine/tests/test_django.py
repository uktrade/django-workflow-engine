from django.conf import settings


def test_config():
    assert settings.DJANGO_WORKFLOWS
