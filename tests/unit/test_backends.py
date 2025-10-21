import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from test_utils.factories import TemporaryPermissionFactory

User = get_user_model()


@pytest.mark.django_db
def test_backend(django_user_model, client):
    can_change_user_permission = Permission.objects.get(codename="change_user")
    user = django_user_model.objects.create_user(username="someone", password="something", is_staff=True)
    client.force_login(user)

    user_view_url = reverse("admin:auth_user_change", kwargs={"object_id": user.id})
    response = client.get(user_view_url)

    assert response.status_code == 403, "User not authenticated, request is denied."

    # Add temporary permission
    TemporaryPermissionFactory(
        user=user,
        permissions=[can_change_user_permission],
    )

    # Verify temporary permission backend provides the permission
    response = client.get(user_view_url)
    assert response.status_code == 200, "Temporary Permission Backend provides permission, allow."
    assert "someone" in response.text
