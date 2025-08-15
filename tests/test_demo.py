import pytest

def test_example():
    assert True


@pytest.mark.django_db
def test_with_db():
    from django.contrib.auth import get_user_model
    User = get_user_model()

    User.objects.create_user(username='test', password='<PASSWORD>')
    assert User.objects.count() == 1
