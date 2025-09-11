"""django-temporary-permissions app config."""

from django.apps import AppConfig
from typing_extensions import override


class Config(AppConfig):  # type: ignore  # noqa D101
    verbose_name = "django-temporary-permissions"
    name = "django_temporary_permissions"

    @override
    def ready(self) -> None:
        pass
