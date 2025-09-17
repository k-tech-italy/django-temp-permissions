"""django-temporary-permissions app config."""

from django.apps import AppConfig
from typing import override


class Config(AppConfig):  # noqa D101
    verbose_name = "django-temporary-permissions"
    name = "django_temporary_permissions"

    @override
    def ready(self) -> None:
        pass
