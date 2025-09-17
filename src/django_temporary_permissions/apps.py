"""django-temporary-permissions app config."""

from django.apps import AppConfig


class Config(AppConfig):  # noqa D101
    verbose_name = "django-temporary-permissions"
    name = "django_temporary_permissions"

    def ready(self) -> None:  # noqa
        pass
