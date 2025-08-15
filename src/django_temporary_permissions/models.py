"""Models for django-temporary-permissions.

This module provides models for managing temporary permissions in Django,
allowing administrators to grant time-limited permissions to users.
"""

from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_temporary_permissions.validators import validate_date_not_in_past


class BaseTemporaryPermission(models.Model):
    """Abstract base model for temporary permissions.

    Provides common fields for all temporary permission types including
    time constraints and optional notes.

    Attributes:
        start_datetime: When the temporary permission becomes active
        end_datetime: When the temporary permission expires
        notes: Optional notes about why the permission was granted

    """

    start_datetime = models.DateTimeField(
        validators=[validate_date_not_in_past], help_text="Date and time when the permission becomes active"
    )
    end_datetime = models.DateTimeField(
        validators=[validate_date_not_in_past], help_text="Date and time when the permission expires"
    )
    notes = models.TextField(null=True, help_text="Optional notes about this temporary permission")

    class Meta:
        abstract = True


class UserTemporaryPermissionQuerySet(models.QuerySet):
    """Custom chained queryset for UserTemporaryPermission."""

    def with_perm(self, permission: Permission) -> QuerySet:
        """Filter to permissions for a specific Permission object."""
        return self.filter(permission=permission)

    def active(self) -> QuerySet:
        """Filter to currently active permissions."""
        now = timezone.now()
        return self.filter(start_datetime__lte=now, end_datetime__gt=now)

    def get_users(self) -> QuerySet:
        """Get actual User objects from the permission records."""
        return get_user_model().objects.filter(id__in=self.values_list("user", flat=True))


class UserTemporaryPermissionManager(models.Manager):
    """Custom manager for UserTemporaryPermission."""

    def get_queryset(self) -> UserTemporaryPermissionQuerySet:  # noqa: D102
        return UserTemporaryPermissionQuerySet(self.model, using=self._db)

    def with_perm(self, permission: Permission) -> QuerySet:  # noqa: D102
        return self.get_queryset().with_perm(permission)

    def active(self) -> QuerySet:  # noqa: D102
        return self.get_queryset().active()

    def get_users(self) -> QuerySet:  # noqa: D102
        return self.get_queryset().get_users()


class UserTemporaryPermission(BaseTemporaryPermission):
    """Temporary permission granted to a specific user.

    Links a user to a permission with time constraints, allowing for
    fine-grained control over temporary access rights.

    Attributes:
        user: The user who receives the temporary permission.
        permission: The Django permission being granted temporarily.

    """

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, help_text="User receiving the temporary permission"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, help_text="The permission being granted temporarily"
    )

    objects = UserTemporaryPermissionManager()

    class Meta:
        unique_together = ("user", "permission", "start_datetime", "end_datetime")
        verbose_name = "Temporary User Permission"
        verbose_name_plural = "Temporary User Permissions"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gte=models.F("start_datetime")),
                name="end_after_start",
            )
        ]

    def __str__(self) -> str:
        """Human-readable representation of the temporary permission."""
        return f"{self.user} - {self.permission} ({self.start_datetime} → {self.end_datetime})"

    def clean(self) -> None:
        """Validate that end_datetime is after start_datetime."""
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be after start datetime.")
