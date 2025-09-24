import pytest
from django.contrib.auth import get_user_model


def test_example():
    assert True


@pytest.mark.django_db
def test_with_db():
    User = get_user_model()  # noqa: N806

    User.objects.create_user(username="test", password="<PASSWORD>")
    assert User.objects.count() == 1
