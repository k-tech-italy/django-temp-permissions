from datetime import timedelta
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError

from django_temporary_permissions.models import UserTemporaryPermission
from .factories import UserFactory, UserTemporaryPermissionFactory, PermissionFactory


@pytest.mark.django_db
def test_with_perm_manager():
    """Test the with_perm manager method with various scenarios."""
    # Use fixed datetime to avoid timing issues
    base_time = timezone.now().replace(microsecond=0)

    # Create test users and permissions
    user_1 = UserFactory()
    user_2 = UserFactory()
    user_3 = UserFactory()

    permission_1 = PermissionFactory()
    permission_2 = PermissionFactory()

    # User 1: Multiple active permissions for permission_1
    UserTemporaryPermissionFactory(
        user=user_1,
        permission=permission_1,
        start_datetime=base_time - timedelta(hours=1),
        end_datetime=base_time + timedelta(hours=1)
    )
    UserTemporaryPermissionFactory(
        user=user_1,
        permission=permission_1,
        start_datetime=base_time - timedelta(minutes=30),
        end_datetime=base_time + timedelta(minutes=30)
    )

    # User 1: Expired and future permissions (should be ignored)
    UserTemporaryPermissionFactory(
        user=user_1,
        permission=permission_1,
        start_datetime=base_time - timedelta(days=5),
        end_datetime=base_time - timedelta(days=2)
    )
    UserTemporaryPermissionFactory(
        user=user_1,
        permission=permission_1,
        start_datetime=base_time + timedelta(hours=2),
        end_datetime=base_time + timedelta(hours=4)
    )

    # User 2: Active permissions for both permission_1 and permission_2
    UserTemporaryPermissionFactory(
        user=user_2,
        permission=permission_1,
        start_datetime=base_time - timedelta(minutes=15),
        end_datetime=base_time + timedelta(hours=2)
    )
    UserTemporaryPermissionFactory(
        user=user_2,
        permission=permission_2,
        start_datetime=base_time - timedelta(minutes=30),
        end_datetime=base_time + timedelta(hours=1)
    )

    # User 3: Only expired permission for permission_1
    UserTemporaryPermissionFactory(
        user=user_3,
        permission=permission_1,
        start_datetime=base_time - timedelta(days=3),
        end_datetime=base_time - timedelta(days=1)
    )

    # Test: Get all users with permission_1 (active only)
    users_with_perm_1 = UserTemporaryPermission.objects.with_perm(permission_1).active().get_users()

    assert users_with_perm_1.count() == 2, "Two users should have active permission_1"

    user_ids = set(users_with_perm_1.values_list("id", flat=True))
    expected_ids = {user_1.id, user_2.id}
    assert user_ids == expected_ids, f"Expected users {expected_ids}, got {user_ids}"

    # Test: Get all users with permission_1 (including inactive)
    all_users_with_perm_1 = UserTemporaryPermission.objects.with_perm(permission_1).get_users()

    assert all_users_with_perm_1.count() == 3, "Three users should have permission_1 records"

    # Test: Get users with permission_2
    users_with_perm_2 = UserTemporaryPermission.objects.with_perm(permission_2).active().get_users()

    assert users_with_perm_2.count() == 1, "Only one user should have active permission_2"
    assert users_with_perm_2.first() == user_2, "User 2 should have permission_2"

    # Test: Empty result for non-existent permission
    unassigned_permission = PermissionFactory()
    empty_result = UserTemporaryPermission.objects.with_perm(unassigned_permission).active().get_users()

    assert empty_result.count() == 0, "Should return no users for unassigned permission"


@pytest.mark.django_db
def test_with_perm_manager_edge_cases():
    """Test edge cases for the with_perm manager."""
    base_time = timezone.now().replace(microsecond=0)

    user_1 = UserFactory()
    user_2 = UserFactory()
    permission = PermissionFactory()

    # Test: Permission that starts exactly now
    UserTemporaryPermissionFactory(
        user=user_1,
        permission=permission,
        start_datetime=base_time,
        end_datetime=base_time + timedelta(hours=1)
    )

    users = UserTemporaryPermission.objects.with_perm(permission).active().get_users()
    assert users.count() == 1, "Permission starting exactly now should be active"

    # Test: Permission that ends exactly now (should not be active)
    UserTemporaryPermissionFactory(
        user=user_2,
        permission=permission,
        start_datetime=base_time - timedelta(hours=1),
        end_datetime=base_time
    )

    users = UserTemporaryPermission.objects.with_perm(permission).active().get_users()
    assert users.count() == 1, "Permission ending exactly now should not be active"


@pytest.mark.django_db
def test_multiple_overlapping_permissions():
    """Test that multiple overlapping permissions for the same user are handled correctly."""
    base_time = timezone.now().replace(microsecond=0)

    user = UserFactory()
    permission = PermissionFactory()

    # Create multiple overlapping active permissions for the same user
    UserTemporaryPermissionFactory(
        user=user,
        permission=permission,
        start_datetime=base_time - timedelta(hours=2),
        end_datetime=base_time + timedelta(hours=2)
    )
    UserTemporaryPermissionFactory(
        user=user,
        permission=permission,
        start_datetime=base_time - timedelta(hours=1),
        end_datetime=base_time + timedelta(hours=3)
    )
    UserTemporaryPermissionFactory(
        user=user,
        permission=permission,
        start_datetime=base_time - timedelta(minutes=30),
        end_datetime=base_time + timedelta(hours=1, minutes=30)
    )

    # Should still count as only one user
    users_with_perm = UserTemporaryPermission.objects.with_perm(permission).active().get_users()

    assert users_with_perm.count() == 1, "Multiple overlapping permissions should count as one user"
    assert users_with_perm.first() == user, "The user should be the expected one"


@pytest.mark.django_db
def test_permission_boundary_conditions():
    """Test permissions at various boundary conditions."""
    base_time = timezone.now().replace(microsecond=0)

    permission = PermissionFactory()

    # Create users with permissions at different boundary conditions
    user_active = UserFactory()
    user_just_expired = UserFactory()
    user_about_to_start = UserFactory()

    # Active permission
    UserTemporaryPermissionFactory(
        user=user_active,
        permission=permission,
        start_datetime=base_time - timedelta(hours=1),
        end_datetime=base_time + timedelta(hours=1)
    )

    # Permission that expired 1 minute ago (safer than 1 second)
    UserTemporaryPermissionFactory(
        user=user_just_expired,
        permission=permission,
        start_datetime=base_time - timedelta(hours=1),
        end_datetime=base_time - timedelta(minutes=1)
    )

    # Permission starting in 1 minute (safer than 1 second)
    UserTemporaryPermissionFactory(
        user=user_about_to_start,
        permission=permission,
        start_datetime=base_time + timedelta(minutes=1),
        end_datetime=base_time + timedelta(hours=1)
    )

    # Only the active permission should be returned
    active_users = UserTemporaryPermission.objects.with_perm(permission).active().get_users()

    assert active_users.count() == 1, "Only one user should have active permission"
    assert active_users.first() == user_active, "Should be the user with active permission"


@pytest.mark.django_db
def test_db_constraint():
    base_time = timezone.now()

    test_user = UserFactory()
    test_permission = PermissionFactory()

    with pytest.raises(IntegrityError):
        UserTemporaryPermissionFactory(
            user=test_user,
            permission=test_permission,
            start_datetime=base_time,
            end_datetime=base_time - timedelta(hours=1)
        )


@pytest.mark.django_db
def test_clean():
    base_time = timezone.now()

    test_user = UserFactory()
    test_permission = PermissionFactory()

    invalid_instance = UserTemporaryPermissionFactory.build(
        user=test_user,
        permission=test_permission,
        start_datetime=base_time,
        end_datetime=base_time - timedelta(hours=1)
    )

    with pytest.raises(ValidationError):
        invalid_instance.full_clean()