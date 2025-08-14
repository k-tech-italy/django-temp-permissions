from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "django_temporary_permissions.core"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from django_temporary_permissions.core import admin  # noqa: F401
