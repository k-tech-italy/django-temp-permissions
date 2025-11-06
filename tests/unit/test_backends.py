import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from test_utils.factories import TemporaryPermissionFactory

User = get_user_model()


@pytest.mark.django_db
def test_backend(staff_user, client):
    can_change_user_permission = Permission.objects.get(codename="change_user")
    client.force_login(staff_user)

    user_view_url = reverse("admin:auth_user_change", kwargs={"object_id": staff_user.id})
    response = client.get(user_view_url)

    assert response.status_code == 403, "User not authenticated, request is denied."

    # Add temporary permission
    TemporaryPermissionFactory(
        user_id=staff_user.id,
        permissions=[can_change_user_permission],
    )

    # Verify temporary permission backend provides the permission
    response = client.get(user_view_url)
    assert response.status_code == 200, "Temporary Permission Backend provides permission, allow."
    assert staff_user.username in response.text
