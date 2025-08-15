"""Admin configuration for django-temporary-permissions."""

from django.contrib import admin
from .models import UserTemporaryPermission


@admin.register(UserTemporaryPermission)
class UserTemporaryPermissionAdmin(admin.ModelAdmin):
    """Admin interface for UserTemporaryPermission model.

    Provides a user-friendly interface for managing temporary permissions
    with filtering, searching, and display customization.
    """

    list_display = (
        "user",
        "user__first_name",
        "user__last_name",
        "permission",
        "start_datetime",
        "end_datetime",
    )
    list_filter = ("user", "start_datetime", "end_datetime")
    search_fields = ("user__username", "user__email")
